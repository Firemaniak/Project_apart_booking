from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError as DRFValidationError

from rest_framework import generics, permissions

from apps.core.permissions import IsOwnerOrReadOnly
from .models import Listing, Photo, Favorite
from .serializers import ListingListSerializer, ListingCreateSerializer, PhotoSerializer, FavoriteSerializer
from rest_framework.response import Response
from django.db.models import Q


class ListingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()

        queryset = Listing.objects.filter(is_active=True)

        search = self.request.query_params.get('search')
        if search:
            from apps.statist.models import SearchHistory
            SearchHistory.objects.create(
                keyword=search,
                user=self.request.user if self.request.user.is_authenticated else None,
            )
            queryset = queryset.filter(
                Q(apartment_name__icontains=search) | Q(description__icontains=search)
            )

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        ordering = self.request.query_params.get('ordering')
        if ordering == 'popular_views':
            queryset = queryset.order_by('-statistic__view_count')
        elif ordering == 'popular_reviews':
            queryset = queryset.order_by('-statistic__reviews_count')

        return queryset




class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ListingCreateSerializer
        return ListingListSerializer


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        from apps.statist.models import ListingStatistic, ListingView

        stat, _ = ListingStatistic.objects.get_or_create(listing=instance)
        stat.view_count += 1
        stat.save(update_fields=['view_count'])

        ListingView.objects.create(
            listing=instance,
            user=request.user if request.user.is_authenticated else None,
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise DRFValidationError("Can't delete a listing that has existing bookings.")


class MyListingListView(generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()

        return Listing.objects.filter(owner=self.request.user)


class PhotoListView(generics.ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.AllowAny]


class PhotoCreateView(generics.CreateAPIView):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PhotoDeleteView(generics.DestroyAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.listing.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete photos from your own listings.")
        instance.delete()


class ListingToggleActiveView(generics.UpdateAPIView):
    queryset = Listing.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def patch(self, request, *args, **kwargs):
        listing = self.get_object()
        listing.is_active = not listing.is_active
        listing.save()
        return Response({'is_active': listing.is_active})



#-----------------------------------------------------------------------------------------------------------------------


class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)