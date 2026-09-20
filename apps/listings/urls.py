from django.urls import path
from .views import (
    ListingListCreateView, ListingDetailView, MyListingListView,
    PhotoListView, PhotoCreateView, PhotoDeleteView, ListingToggleActiveView
)

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list-create'),
    path('my/', MyListingListView.as_view(), name='my-listings'),
    path('<uuid:pk>/toggle-active/', ListingToggleActiveView.as_view(), name='listing-toggle-active'),
    path('<uuid:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('photos/', PhotoListView.as_view(), name='photo-list'),
    path('photos/create/', PhotoCreateView.as_view(), name='photo-create'),
    path('photos/<uuid:pk>/delete/', PhotoDeleteView.as_view(), name='photo-delete'),
]