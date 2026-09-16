from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer, ReviewOwnerResponseSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewListSerializer


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.AllowAny]


class ReviewOwnerResponseView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewOwnerResponseSerializer
    permission_classes = [permissions.IsAuthenticated]