from django.urls import path
from .views import BookingListCreateView, BookingDetailView, ListingBookedDatesView, BookingPaymentView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('<uuid:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('listing/<uuid:listing_id>/booked-dates/', ListingBookedDatesView.as_view(), name='listing-booked-dates'),
    path('<uuid:pk>/pay/', BookingPaymentView.as_view(), name='booking-pay'),
]