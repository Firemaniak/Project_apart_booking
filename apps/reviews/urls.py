from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView, ReviewOwnerResponseView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-list-create'),
    path('<uuid:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('<uuid:pk>/response/', ReviewOwnerResponseView.as_view(), name='review-owner-response'),
]