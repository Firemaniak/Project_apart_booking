from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError as DRFValidationError

from rest_framework import generics, permissions

from apps.core.permissions import IsOwnerOrReadOnly
from .models import Listing, Photo, Favorite
from .serializers import ListingListSerializer, ListingCreateSerializer, PhotoSerializer, FavoriteSerializer
from rest_framework.response import Response
from django.db.models import Q


class ListingListCreateView(generics.ListCreateAPIView):
    """
    Public listing catalog with search, price filtering, and popularity
    sorting; also handles listing creation.

    Anyone can browse the catalog (``IsAuthenticatedOrReadOnly``);
    only authenticated users can create listings. Each search query
    is logged to ``SearchHistory`` for the "popular searches" feature.

    Публичный каталог объявлений с поиском, фильтром по цене и
    сортировкой по популярности; также обрабатывает создание листинга.

    Просматривать каталог может кто угодно
    (``IsAuthenticatedOrReadOnly``); создавать листинги — только
    авторизованные пользователи. Каждый поисковый запрос логируется
    в ``SearchHistory`` для функции "популярные запросы".
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingListSerializer

    def perform_create(self, serializer):
        """
        Attach the authenticated user as owner — never accepted from
        the request body.

        Проставляет авторизованного пользователя как владельца —
        никогда не принимается из тела запроса.
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Build the catalog queryset from active listings, applying
        optional search, price range, and popularity ordering based
        on query parameters.

        Строит queryset каталога из активных листингов, применяя
        опциональный поиск, диапазон цен и сортировку по популярности
        на основе query-параметров.
        """
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
    """
    Retrieve, edit, or delete a single listing.

    Anyone can view a listing; only its owner can edit or delete it
    (``IsOwnerOrReadOnly``). Editing reuses ``ListingCreateSerializer``,
    since it accepts the same fields as creation.

    Просмотр, редактирование или удаление одного листинга.

    Просматривать может кто угодно; редактировать/удалять — только
    владелец (``IsOwnerOrReadOnly``). Для редактирования переиспользуется
    ``ListingCreateSerializer``, так как он принимает те же поля, что
    и создание.
    """
    queryset = Listing.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ListingCreateSerializer
        return ListingListSerializer


    def retrieve(self, request, *args, **kwargs):
        """
        Increment the listing's view counter and log an individual
        view record each time the listing is opened — used for the
        "popular listings" and view-history features.

        Увеличивает счётчик просмотров листинга и логирует отдельную
        запись просмотра при каждом открытии листинга — используется
        для функций "популярные объявления" и истории просмотров.
        """
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
        """
        Turn a raw ProtectedError (from bookings referencing this
        listing with on_delete=PROTECT) into a clean API error message.

        Превращает голый ProtectedError (от броней, ссылающихся на
        этот листинг через on_delete=PROTECT) в понятное сообщение
        об ошибке API.
        """
        try:
            instance.delete()
        except ProtectedError:
            raise DRFValidationError("Can't delete a listing that has existing bookings.")


class MyListingListView(generics.ListAPIView):
    """
    Lists only the authenticated user's own listings, including
    inactive (hidden) ones — used for the host's "my listings" page.

    Показывает только собственные листинги авторизованного
    пользователя, включая неактивные (скрытые) — используется для
    страницы "мои объявления" хозяина.
    """
    serializer_class = ListingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()

        return Listing.objects.filter(owner=self.request.user)


class PhotoListView(generics.ListAPIView):
    """
    Public list of all photos — mainly useful for debugging/admin
    purposes, since photos are normally accessed nested under a
    listing.

    Публичный список всех фото — в основном полезен для отладки,
    так как обычно фото доступны вложенными в листинг.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.AllowAny]


class PhotoCreateView(generics.CreateAPIView):
    """
    Uploads a new photo for a listing. Ownership of the target listing
    is validated in ``PhotoSerializer.validate_listing()``.

    Загружает новое фото для листинга. Владение целевым листингом
    проверяется в ``PhotoSerializer.validate_listing()``.
    """
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PhotoDeleteView(generics.DestroyAPIView):
    """
    Deletes a photo. Only the owner of the listing the photo belongs
    to may delete it.

    Удаляет фото. Удалить его может только владелец листинга,
    которому принадлежит фото.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.listing.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete photos from your own listings.")
        instance.delete()


class ListingToggleActiveView(generics.UpdateAPIView):
    """
    Flips a listing's is_active flag, letting the host hide or
    re-show it in the public catalog without deleting it.

    Переключает флаг is_active листинга, позволяя хозяину скрыть или
    снова показать его в публичном каталоге, не удаляя.
    """
    queryset = Listing.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def patch(self, request, *args, **kwargs):
        listing = self.get_object()
        listing.is_active = not listing.is_active
        listing.save()
        return Response({'is_active': listing.is_active})



#-----------------------------------------------------------------------------------------------------------------------


class FavoriteListCreateView(generics.ListCreateAPIView):
    """
    Lists the authenticated user's favorited listings and creates
    new favorites.

    Показывает избранные листинги авторизованного пользователя
    и создаёт новые записи избранного.
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Attach the authenticated user — never accepted from the
        request body, so a user can only favorite listings on their
        own behalf.

        Проставляет авторизованного пользователя — никогда не
        принимается из тела запроса, чтобы добавлять в избранное
        можно было только от своего имени.
        """
        serializer.save(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    """
    Removes a listing from the authenticated user's favorites.

    The queryset is scoped to the current user, so a user cannot
    delete someone else's favorite by guessing its id.

    Убирает листинг из избранного авторизованного пользователя.

    Queryset ограничен текущим пользователем, чтобы нельзя было
    удалить чужую запись избранного, подобрав её id.
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)