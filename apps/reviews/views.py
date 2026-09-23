from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer, ReviewOwnerResponseSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    Public list of all reviews, and review creation.

    Anyone can read reviews (``IsAuthenticatedOrReadOnly``); creating
    one requires authentication, with the additional guest/timing
    checks enforced in ``ReviewCreateSerializer``.

    Публичный список всех отзывов и их создание.

    Читать отзывы может кто угодно (``IsAuthenticatedOrReadOnly``);
    для создания нужна авторизация, а дополнительные проверки
    (гость/сроки) выполняются в ``ReviewCreateSerializer``.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewListSerializer


class ReviewDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single review by id. Public — no authentication
    required, since reviews are meant to be visible to any visitor
    browsing a listing.

    Получение одного отзыва по id. Публично — авторизация не
    требуется, так как отзывы должны быть видны любому посетителю,
    просматривающему листинг.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.AllowAny]


class ReviewOwnerResponseView(generics.UpdateAPIView):
    """
    Lets a listing's owner respond to a review left on their listing.

    Ownership of the reviewed listing is validated inside
    ``ReviewOwnerResponseSerializer``, not here — permission_classes
    only checks that *some* user is authenticated.

    Позволяет владельцу листинга ответить на отзыв, оставленный на
    его листинг.

    Проверка владения листингом, на который оставлен отзыв,
    выполняется внутри ``ReviewOwnerResponseSerializer``, а не здесь —
    permission_classes проверяет только то, что пользователь вообще
    авторизован.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewOwnerResponseSerializer
    permission_classes = [permissions.IsAuthenticated]