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


class ListingModelTests(TestCase):
    """
    Tests for Listing model validation logic.

    Тесты валидации модели Listing.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass12345',
            address='Test address',
        )

    def _base_listing_kwargs(self, **overrides):
        """
        Shared minimal set of valid fields for constructing a Listing
        in tests, with the option to override individual fields.

        Общий минимальный набор валидных полей для создания Listing
        в тестах, с возможностью переопределить отдельные поля.
        """
        kwargs = dict(
            apartment_name='Test Apartment',
            address='Teststraße 1, Berlin',
            country='DE',
            max_guests=4,
            room_count=2,
            shower_count=1,
            toilets_count=1,
            property_type='apartment',
            floor=2,
            price_per_night=Decimal('50.00'),
            owner=self.owner,
        )
        kwargs.update(overrides)
        return kwargs

    def test_house_without_floors_count_is_invalid(self):
        """A house listing must specify floors_count, not floor."""
        listing = Listing(**self._base_listing_kwargs(
            property_type='house', floor=None, floors_count=None,
        ))
        with self.assertRaises(ValidationError):
            listing.clean()

    def test_house_with_floors_count_is_valid(self):
        """A house listing with floors_count set should pass validation."""
        listing = Listing(**self._base_listing_kwargs(
            property_type='house', floor=None, floors_count=2,
        ))
        listing.clean()  # should not raise

    def test_apartment_without_floor_is_invalid(self):
        """A non-house listing must specify floor."""
        listing = Listing(**self._base_listing_kwargs(floor=None))
        with self.assertRaises(ValidationError):
            listing.clean()

    def test_listing_str_representation(self):
        """__str__ should include the apartment name."""
        listing = Listing.objects.create(**self._base_listing_kwargs())
        self.assertIn('Test Apartment', str(listing))


class ListingAPITests(TestCase):
    """
    Integration tests for listing endpoints: creation, ownership
    permissions, and the active/hidden toggle.

    Интеграционные тесты эндпоинтов листингов: создание, права
    владения, переключение активности.
    """

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass12345',
            address='Test address',
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass12345',
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
            property_type='apartment',
            floor=2,
            price_per_night=Decimal('50.00'),
            owner=self.owner,
        )

    def test_authenticated_user_can_create_listing(self):
        """An authenticated user should be able to create a listing,
        and it should be attributed to them as owner."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/listings/', {
            'apartment_name': 'New Listing',
            'address': 'Neue Straße 5, Berlin',
            'country': 'DE',
            'max_guests': 2,
            'room_count': 1,
            'shower_count': 1,
            'toilets_count': 1,
            'property_type': 'apartment',
            'floor': 1,
            'price_per_night': '40.00',
            'input_type': 'key',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Listing.objects.get(apartment_name='New Listing')
        self.assertEqual(created.owner, self.owner)

    def test_unauthenticated_user_cannot_create_listing(self):
        """Anonymous users should not be able to create listings."""
        response = self.client.post('/api/listings/', {
            'apartment_name': 'New Listing',
            'address': 'Neue Straße 5, Berlin',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_owner_cannot_edit_listing(self):
        """A user who does not own the listing should not be able to edit it."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f'/api/listings/{self.listing.id}/', {
            'apartment_name': 'Hacked Name',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_edit_own_listing(self):
        """The listing owner should be able to edit it."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(f'/api/listings/{self.listing.id}/', {
            'apartment_name': 'Updated Name',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.apartment_name, 'Updated Name')

    def test_toggle_active_hides_listing_from_catalog(self):
        """Toggling a listing to inactive should remove it from the
        public catalog while it remains visible to its owner."""
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(f'/api/listings/{self.listing.id}/toggle-active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_active)

        catalog_response = self.client.get('/api/listings/')
        listing_ids = [item['id'] for item in catalog_response.data]
        self.assertNotIn(str(self.listing.id), listing_ids)

    def test_cannot_delete_listing_with_active_booking(self):
        """Deleting a listing that has an existing booking should be
        rejected, since bookings are protected (on_delete=PROTECT)."""
        guest = User.objects.create_user(
            username='guest', email='guest@example.com', password='pass12345',
            address='Test address',
        )
        now = timezone.localtime(timezone.now())
        Booking.objects.create(
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=3),
            guests_count=2,
            guest=guest,
            listing=self.listing,
        )

        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)