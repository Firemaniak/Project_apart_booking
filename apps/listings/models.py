from django.db import models

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.conf import settings

from apps.core.models import UniqueID, TimeStampedModel

from simple_history.models import HistoricalRecords


#-----------------------------------------------------------------------------------------------------------------------

class InputTypeChoices(models.TextChoices):
    """
    How a guest gains access to the listing.

    Способ, которым гость попадает в листинг.
    """
    with_key = 'key', _('Key')
    with_pin_kode = 'pin_kode', _('Pin_kode')
    with_card = 'card', _('Card')


class PropertyTypeChoices(models.TextChoices):
    """
    The type of property being listed.

    Only ``house`` listings use ``floors_count``; ``apartment`` and
    ``studio`` use ``floor`` instead — enforced in ``Listing.clean()``.

    Тип объявляемого жилья.

    Только для ``house`` используется ``floors_count``; для
    ``apartment`` и ``studio`` — ``floor``; проверяется
    в ``Listing.clean()``.
    """
    apartment = 'apartment', _('Apartment')
    house = 'house', _('House')
    studio = 'studio', _('Studio')

class CountryChoices(models.TextChoices):
    """
    Supported countries for listings. Only Germany is offered, since
    the platform is scoped to the German rental market.

    Поддерживаемые страны для объявлений. Доступна только Германия,
    так как платформа ориентирована на немецкий рынок аренды.
    """
    germany = 'DE', _('Germany')


#-----------------------------------------------------------------------------------------------------------------------


class Listing(UniqueID, TimeStampedModel):
    """
    A property available for short-term rental, owned by a host.

    ``owner`` uses ``on_delete=PROTECT`` — a user cannot be deleted
    while they still own listings, preserving booking/review history.
    ``is_active`` lets a host hide a listing from the public catalog
    without deleting it. Full change history is tracked via
    ``simple_history`` (``HistoricalRecords``).

    Объект недвижимости, доступный для краткосрочной аренды,
    принадлежащий хозяину.

    ``owner`` использует ``on_delete=PROTECT`` — пользователя нельзя
    удалить, пока у него есть листинги, это сохраняет историю
    броней/отзывов. ``is_active`` позволяет хозяину скрыть листинг
    из публичного каталога, не удаляя его. Полная история изменений
    отслеживается через ``simple_history`` (``HistoricalRecords``).
    """
    apartment_name = models.CharField(max_length=30, validators=[MinLengthValidator(3)],
                                  verbose_name='apartment name')
    description = models.TextField(blank=True,
                                   verbose_name='description')
    address = models.CharField(max_length=60, validators=[MinLengthValidator(5)],
                                 verbose_name='address')
    floor = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(165)],null=True, blank=True,
                                 verbose_name='floor')
    country = models.CharField(max_length=2, choices=CountryChoices, default=CountryChoices.germany,
                               verbose_name='country')
    max_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                                  verbose_name='maximum number of guests')
    floors_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True, verbose_name='number of floors')
    room_count = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(20)],
                                 verbose_name='number of rooms')
    shower_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                  verbose_name='number of shower rooms')
    toilets_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                    verbose_name='number of toilets')
    input_type = models.CharField(max_length=10, choices=InputTypeChoices, default=InputTypeChoices.with_key,
                                  verbose_name='how to get in')
    parking = models.BooleanField(default=False,
                                  verbose_name='availability of parking')

    can_smoke = models.BooleanField(default=False,
                                    verbose_name='Is smoking allowed?')
    wifi = models.BooleanField(default=False,
                               verbose_name= 'Wi-Fi')
    indoor_fireplace = models.BooleanField(default=False,
                                           verbose_name='Is there a fireplace')
    can_pets = models.BooleanField(default=False,
                                   verbose_name='Are pets allowed?')
    facilities_for_guests_with_disabilities = models.BooleanField(default=False,
                                                                  verbose_name='Accessibility for people with '
                                                                               'disabilities?')
    air_conditioner = models.BooleanField(default=False,
                                          verbose_name='Is there air conditioning?')
    elevator = models.BooleanField(default=False,
                                   verbose_name='Is there an elevator?')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='listings')

    price_per_night = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='price per night'
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    property_type = models.CharField(
        max_length=15, choices=PropertyTypeChoices, default=PropertyTypeChoices.apartment,
        verbose_name='property type'
    )

    is_active = models.BooleanField(default=True, verbose_name='is active')

    history = HistoricalRecords()

    def __str__(self):
        return f'Apartment: {self.apartment_name}, {self.country}, {self.room_count} rooms'

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['apartment_name', 'country', 'room_count']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['price_per_night']),
        ]

    def clean(self):
        """
        Enforce that houses specify floors_count while other property
        types specify floor — the two fields are mutually exclusive
        by design, matching how each type of property is described.

        Требует, чтобы дома указывали floors_count, а остальные типы
        жилья — floor; эти два поля взаимоисключающие по замыслу,
        отражая то, как описывается каждый тип недвижимости.
        """
        super().clean()
        if self.property_type == PropertyTypeChoices.house:
            if self.floors_count is None:
                raise ValidationError({'floors_count': 'This field is required for houses.'})
        else:
            if self.floor is None:
                raise ValidationError({'floor': 'This field is required for apartments and rooms.'})


#-----------------------------------------------------------------------------------------------------------------------


class Photo(UniqueID, TimeStampedModel):
    """
    A single photo belonging to a listing's gallery.

    Deleted automatically (``on_delete=CASCADE``) when its listing is
    deleted, since a photo has no meaning without the listing it
    illustrates.

    Одна фотография из галереи листинга.

    Удаляется автоматически (``on_delete=CASCADE``) вместе с листингом,
    так как фото не имеет смысла без листинга, который оно иллюстрирует.
    """
    image = models.ImageField(upload_to='listing_photos/')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')

    def __str__(self):
        return f'Photo for {self.listing.apartment_name}'

    class Meta:
        db_table = 'photos'
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['created_at']



#-----------------------------------------------------------------------------------------------------------------------


class Favorite(UniqueID, TimeStampedModel):
    """
    A user's bookmark of a listing they're interested in.

    ``unique_together`` prevents a user from favoriting the same
    listing twice. Uses ``CASCADE`` on both sides, since a favorite
    is derived data with no meaning once either the user or the
    listing is gone.

    Закладка пользователя на понравившийся ему листинг.

    ``unique_together`` не даёт пользователю добавить один и тот же
    листинг в избранное дважды. Использует ``CASCADE`` с обеих сторон,
    так как избранное — производные данные, не имеющие смысла после
    удаления пользователя или листинга.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.listing.apartment_name}'