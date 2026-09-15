from django.db.models import Q
from rest_framework import generics, permissions

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