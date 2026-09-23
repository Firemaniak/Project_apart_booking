from .models import Booking
from rest_framework import serializers
from django.utils import timezone


#-----------------------------------------------------------------------------------------------------------------------


class BookingListSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a booking, used for list and detail views.

    ``price`` and ``status`` are read-only: price is calculated by the
    model, and status changes only through the payment/cancellation flow,
    never through direct edits.

    Представление брони для чтения — используется для списков и деталей.

    ``price`` и ``status`` доступны только для чтения: цена вычисляется
    моделью, а статус меняется только через оплату/отмену, но не через
    прямое редактирование.
    """
    class Meta:
        model = Booking
        fields = ['id', 'start_date', 'end_date', 'price', 'payment_type',
                  'guests_count', 'guest', 'listing', 'status', 'created_at']
        read_only_fields = ['price', 'status']


#----------------------              ------------------------------              ---------------------------------------


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Validates and creates a new booking.

    ``guest`` is intentionally excluded from the fields — it is set from
    the authenticated request user in the view, never accepted from the
    client, so a guest cannot create a booking on someone else's behalf.

    Валидирует и создаёт новую бронь.

    Поле ``guest`` намеренно отсутствует в списке полей — оно
    проставляется из авторизованного пользователя во вьюхе, а не
    принимается от клиента, чтобы гость не мог создать бронь от чужого
    имени.
    """
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'payment_type', 'guests_count', 'listing']

    def validate(self, attrs):
        """
        Cross-field validation: dates, availability, guest capacity,
        and self-booking prevention.

        Only bookings with ``status='paid'`` count as occupying the
        dates, so a pending (unpaid) booking does not block other guests
        from booking the same dates.

        Комплексная валидация: даты, доступность, вместимость и защита
        от бронирования собственного листинга.

        Датами считаются занятыми только брони со статусом ``'paid'``,
        поэтому неоплаченная (pending) бронь не блокирует эти даты
        для других гостей.
        """
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError('The end date must be later than the start date.')

        if attrs['start_date'].date() < timezone.localtime(timezone.now()).date():
            raise serializers.ValidationError('Start date cannot be in the past.')

        overlapping = Booking.objects.filter(
            listing=attrs['listing'],
            status='paid',
            start_date__lt=attrs['end_date'],
            end_date__gt=attrs['start_date'],
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError('This listing is already booked for the selected dates.')

        if attrs['guests_count'] > attrs['listing'].max_guests:
            raise serializers.ValidationError(
                f"This listing allows up to {attrs['listing'].max_guests} guests."
            )

        request = self.context.get('request')
        if request and attrs['listing'].owner == request.user:
            raise serializers.ValidationError("You can't book your own listing.")

        return attrs


#-----------------------------------------------------------------------------------------------------------------------


class PaymentSerializer(serializers.Serializer):
    """
    Validates simulated card payment details for a booking.

    This is not a real payment gateway integration — it only checks
    that the submitted data has a valid format (card number length,
    expiry date, CVV). Card number and CVV are ``write_only`` and are
    never stored in full; only the last 4 digits of the card are kept
    on the booking, in ``Booking.card_last4``.

    Валидирует данные симулированной оплаты картой для брони.

    Это не интеграция с реальным платёжным шлюзом — проверяется только
    формат введённых данных (длина номера карты, срок действия, CVV).
    Номер карты и CVV помечены ``write_only`` и никогда не сохраняются
    целиком; на брони хранятся только последние 4 цифры карты,
    в поле ``Booking.card_last4``.
    """
    cardholder_name = serializers.CharField(max_length=100)
    card_number = serializers.CharField(max_length=19, write_only=True)
    expiry_date = serializers.CharField(max_length=5, write_only=True)  # MM/YY
    cvv = serializers.CharField(max_length=4, write_only=True)

    def validate_card_number(self, value):
        """
        Strip spaces/dashes and check the digit length looks like
        a real card number (13–19 digits).

        Убирает пробелы/дефисы и проверяет, что длина цифр похожа
        на реальный номер карты (13–19 цифр).
        """
        digits = value.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 13 or len(digits) > 19:
            raise serializers.ValidationError('Invalid card number.')
        return digits

    def validate_expiry_date(self, value):
        """
        Check the MM/YY format and reject already-expired cards.

        Проверяет формат MM/YY и отклоняет уже просроченные карты.
        """
        import re
        if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', value):
            raise serializers.ValidationError('Expiry date must be in MM/YY format.')

        from datetime import datetime
        month, year = value.split('/')
        expiry = datetime(2000 + int(year), int(month), 1)
        if expiry < datetime.now().replace(day=1):
            raise serializers.ValidationError('Card has expired.')
        return value

    def validate_cvv(self, value):
        """
        CVV must be 3 or 4 numeric digits.

        CVV должен состоять из 3 или 4 цифр.
        """
        if not value.isdigit() or len(value) not in (3, 4):
            raise serializers.ValidationError('Invalid CVV.')
        return value

    def validate_cardholder_name(self, value):
        """
        Require at least a first and last name.

        Требует как минимум имя и фамилию.
        """
        if len(value.strip().split()) < 2:
            raise serializers.ValidationError('Enter full name (first and last name).')
        return value