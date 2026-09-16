from rest_framework import generics, permissions

from .models import ListingStatistic, UserStatistic
from .serializers import ListingStatisticSerializer, UserStatisticSerializer


class ListingStatisticDetailView(generics.RetrieveAPIView):
    queryset = ListingStatistic.objects.all()
    serializer_class = ListingStatisticSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'listing_id'


class UserStatisticDetailView(generics.RetrieveAPIView):
    """Публичная статистика юзера — рейтинг и активность, без денег"""
    queryset = UserStatistic.objects.all()
    serializer_class = UserStatisticSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user_id'
