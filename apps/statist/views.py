from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ListingStatistic, UserStatistic
from .serializers import ListingStatisticSerializer, UserStatisticSerializer
from django.db.models import Count
from .models import SearchHistory

class PopularSearchesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        popular = (
            SearchHistory.objects
            .values('keyword')
            .annotate(count=Count('keyword'))
            .order_by('-count')[:10]
        )
        return Response(list(popular))




class ListingStatisticDetailView(generics.RetrieveAPIView):
    """Публичная статистика листингов"""
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
