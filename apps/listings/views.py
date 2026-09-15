from rest_framework import generics, permissions

from apps.core.permissions import IsOwnerOrReadOnly
from .models import Listing
from .serializers import ListingListSerializer, ListingCreateSerializer


class ListingListCreateView(generics.ListCreateAPIView):
    queryset = Listing.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]
