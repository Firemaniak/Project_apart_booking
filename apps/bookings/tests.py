from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.listings.models import Listing
from apps.bookings.models import Booking

User = get_user_model()


#-----------------------------------------------------------------------------------------------------------------------


class BookingModelTests(TestCase):

    """
    Tests for Booking model validation and price calculation logic.

    Тесты валидации модели Booking и логики расчёта цены.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass12345',
            address='Test address',
        )
        self.guest = User.objects.create_user(
            username='guest', email='guest@example.com', password='pass12345',
            address='Test address',
        )
        self.listing = Listing.objects.create(
            apartment_name='Test Apartment',
            address='Teststraße 1, Berlin',
            country='DE',
            max_guests=4,
            room_count=2,
            shower_count=1,
            toilets_count=1,
            floor=2,
            price_per_night=Decimal('50.00'),
            owner=self.owner,
        )
        self.now = timezone.localtime(timezone.now())

    def test_price_is_calculated_automatically(self):

        """Price should be nights × price_per_night when not provided."""

        booking = Booking.objects.create(
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=4),
            guests_count=2,
            guest=self.guest,
            listing=self.listing,
        )
        self.assertEqual(booking.price, Decimal('150.00'))  # 3 nights * 50


    def test_end_date_before_start_date_is_invalid(self):

        """clean() should reject an end date earlier than the start date."""

        booking = Booking(
            start_date=self.now + timedelta(days=3),
            end_date=self.now + timedelta(days=1),
            guests_count=1,
            guest=self.guest,
            listing=self.listing,
        )
        with self.assertRaises(ValidationError):
            booking.clean()


    def test_overlapping_paid_booking_is_rejected(self):

        """A new booking overlapping an existing paid one should fail validation."""

        Booking.objects.create(
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=5),
            guests_count=1,
            guest=self.guest,
            listing=self.listing,
            status='paid',
        )
        overlapping = Booking(
            start_date=self.now + timedelta(days=3),
            end_date=self.now + timedelta(days=6),
            guests_count=1,
            guest=self.guest,
            listing=self.listing,
        )
        with self.assertRaises(ValidationError):
            overlapping.clean()


class BookingAPITests(TestCase):

    """
    Integration tests for the booking creation API endpoint.

    Интеграционные тесты для эндпоинта создания брони.
    """

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass12345',
            address='Test address',
        )
        self.guest = User.objects.create_user(
            username='guest', email='guest@example.com', password='pass12345',
            address='Test address',
        )
        self.listing = Listing.objects.create(
            apartment_name='Test Apartment',
            address='Teststraße 1, Berlin',
            country='DE',
            max_guests=4,
            room_count=2,
            shower_count=1,
            toilets_count=1,
            floor=2,
            price_per_night=Decimal('50.00'),
            owner=self.owner,
        )
        self.now = timezone.localtime(timezone.now())


    def test_owner_cannot_book_own_listing(self):

        """A listing owner should not be able to book their own listing."""

        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'start_date': (self.now + timedelta(days=1)).isoformat(),
            'end_date': (self.now + timedelta(days=3)).isoformat(),
            'guests_count': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_guest_can_create_booking(self):

        """An authenticated guest should be able to book someone else's listing."""

        self.client.force_authenticate(user=self.guest)
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'start_date': (self.now + timedelta(days=1)).isoformat(),
            'end_date': (self.now + timedelta(days=3)).isoformat(),
            'guests_count': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_unauthenticated_user_cannot_book(self):

        """Anonymous users should not be able to create a booking."""

        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'start_date': (self.now + timedelta(days=1)).isoformat(),
            'end_date': (self.now + timedelta(days=3)).isoformat(),
            'guests_count': 2,
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
