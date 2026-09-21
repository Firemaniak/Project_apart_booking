import logging
from django.utils import timezone

from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.core.permissions import IsBookingParticipant
from .models import Booking, BookingStatusChoices
from .serializers import BookingListSerializer, BookingCreateSerializer, PaymentSerializer


#-----------------------------------------------------------------------------------------------------------------------


logger = logging.getLogger('apps.bookings')


class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_create(self, serializer):
        booking = serializer.save(guest=self.request.user)
        logger.info(f'Booking {booking.id} created by {self.request.user.username} for listing {booking.listing.id}')


class BookingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsBookingParticipant]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_destroy(self, instance):
        if instance.end_date < timezone.now():
            raise DRFValidationError("Can't cancel a booking that has already ended.")
        try:
            instance.delete()
        except ProtectedError:
            raise DRFValidationError("Can't cancel a booking that already has a review.")


class ListingBookedDatesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, listing_id):
        bookings = Booking.objects.filter(
            listing_id=listing_id, status=BookingStatusChoices.paid
        ).values('start_date', 'end_date')
        booked_ranges = [
            {'from': b['start_date'].date(), 'to': b['end_date'].date()}
            for b in bookings
        ]
        return Response(booked_ranges)



#-----------------------------------------------------------------------------------------------------------------------


class BookingPaymentView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, guest=request.user)

        if booking.status != BookingStatusChoices.pending:
            return Response({'detail': 'This booking is not pending payment.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_number = serializer.validated_data['card_number']
        booking.card_last4 = card_number[-4:]
        booking.status = BookingStatusChoices.paid
        booking.save(update_fields=['card_last4', 'status'])

        send_mail(
            subject='Booking payment confirmed',
            message=f'Your booking for {booking.listing.apartment_name} has been paid. Amount: {booking.price} €.',
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=True,
        )

        return Response({
            'status': 'paid',
            'message': 'Payment successful. A confirmation has been sent to your email.',
            'card_last4': booking.card_last4,
        })