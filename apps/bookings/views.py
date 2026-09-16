from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.core.permissions import IsBookingParticipant
from .models import Booking
from .serializers import BookingListSerializer, BookingCreateSerializer


#-----------------------------------------------------------------------------------------------------------------------


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)


class BookingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsBookingParticipant]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise DRFValidationError("Can't cancel a booking that already has a review.")


class ListingBookedDatesView(APIView):
    """Отдаёт список занятых диапазонов дат для конкретного листинга — для фронтенд-календаря."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, listing_id):
        bookings = Booking.objects.filter(listing_id=listing_id).values('start_date', 'end_date')
        booked_ranges = [
            {'from': b['start_date'].date(), 'to': b['end_date'].date()}
            for b in bookings
        ]
        return Response(booked_ranges)