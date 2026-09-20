from django.urls import path
from .views import ListingStatisticDetailView, UserStatisticDetailView, PopularSearchesView

urlpatterns = [
    path('listing/<uuid:listing_id>/', ListingStatisticDetailView.as_view(), name='listing-statistic'),
    path('user/<int:user_id>/', UserStatisticDetailView.as_view(), name='user-statistic'),
    path('popular-searches/', PopularSearchesView.as_view(), name='popular-searches'),
]