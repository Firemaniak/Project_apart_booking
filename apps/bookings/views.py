# import logging
# from django.utils import timezone
#
# from django.core.mail import send_mail
# from django.db.models import Q
# from django.db.models.deletion import ProtectedError
# from rest_framework import generics, permissions
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError as DRFValidationError
#
# from apps.core.permissions import IsBookingParticipant
# from .models import Booking, BookingStatusChoices
# from .serializers import BookingListSerializer, BookingCreateSerializer, PaymentSerializer
#
#
# #-----------------------------------------------------------------------------------------------------------------------
#
#
# logger = logging.getLogger('apps.bookings')
#
#
# class BookingListCreateView(generics.ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return BookingCreateSerializer
#         return BookingListSerializer
#
#     def get_queryset(self):
#
#         if getattr(self, 'swagger_fake_view', False):
#             return Booking.objects.none()
#
#         user = self.request.user
#         return Booking.objects.filter(
#             Q(guest=user) | Q(listing__owner=user)
#         ).select_related('listing', 'guest')
#
#     def perform_create(self, serializer):
#         booking = serializer.save(guest=self.request.user)
#         logger.info(f'Booking {booking.id} created by {self.request.user.username} for listing {booking.listing.id}')
#
#
# class BookingDetailView(generics.RetrieveDestroyAPIView):
#     serializer_class = BookingListSerializer
#     permission_classes = [IsBookingParticipant]
#
#     def get_queryset(self):
#
#         if getattr(self, 'swagger_fake_view', False):
#             return Booking.objects.none()
#
#         user = self.request.user
#         return Booking.objects.filter(
#             Q(guest=user) | Q(listing__owner=user)
#         ).select_related('listing', 'guest')
#
#     def perform_destroy(self, instance):
#         if instance.end_date < timezone.now():
#             raise DRFValidationError("Can't cancel a booking that has already ended.")
#         try:
#             instance.delete()
#         except ProtectedError:
#             raise DRFValidationError("Can't cancel a booking that already has a review.")
#
#
# class ListingBookedDatesView(APIView):
#     permission_classes = [permissions.AllowAny]
#
#     def get(self, request, listing_id):
#         bookings = Booking.objects.filter(
#             listing_id=listing_id, status=BookingStatusChoices.paid
#         ).values('start_date', 'end_date')
#         booked_ranges = [
#             {'from': b['start_date'].date(), 'to': b['end_date'].date()}
#             for b in bookings
#         ]
#         return Response(booked_ranges)
#
#
#
# #-----------------------------------------------------------------------------------------------------------------------
#
#
# class BookingPaymentView(generics.GenericAPIView):
#     serializer_class = PaymentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         booking = get_object_or_404(Booking, pk=pk, guest=request.user)
#
#         if booking.status != BookingStatusChoices.pending:
#             return Response({'detail': 'This booking is not pending payment.'}, status=400)
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         card_number = serializer.validated_data['card_number']
#         booking.card_last4 = card_number[-4:]
#         booking.status = BookingStatusChoices.paid
#         booking.save(update_fields=['card_last4', 'status'])
#
#         send_mail(
#             subject='Booking payment confirmed',
#             message=f'Your booking for {booking.listing.apartment_name} has been paid. Amount: {booking.price} €.',
#             from_email=None,
#             recipient_list=[request.user.email],
#             fail_silently=True,
#         )
#
#         return Response({
#             'status': 'paid',
#             'message': 'Payment successful. A confirmation has been sent to your email.',
#             'card_last4': booking.card_last4,
#         })



import logging
from django.utils import timezone

from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.core.permissions import IsBookingParticipant
from .models import Booking, BookingStatusChoices
from .serializers import BookingListSerializer, BookingCreateSerializer, PaymentSerializer


#-----------------------------------------------------------------------------------------------------------------------


logger = logging.getLogger('apps.bookings')


class BookingListCreateView(generics.ListCreateAPIView):
    """
    List the current user's bookings (as guest or as listing owner)
    and create new bookings.

    A user sees a booking if they are either the guest who made it or
    the owner of the listing it was made on — so hosts can see incoming
    reservations without a separate endpoint.

    Список броней текущего пользователя (как гостя или как владельца
    листинга) и создание новых броней.

    Пользователь видит бронь, если он либо гость, создавший её, либо
    владелец листинга, на который она сделана — так хозяева видят
    входящие брони без отдельного эндпоинта.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer

    def get_queryset(self):
        """
        Return bookings where the user is either the guest or the
        owner of the booked listing.

        Возвращает брони, где пользователь — либо гость, либо
        владелец забронированного листинга.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_create(self, serializer):
        """
        Attach the authenticated user as the guest — never accepted
        from the request body, so a user cannot book on someone
        else's behalf.

        Проставляет авторизованного пользователя как гостя — никогда
        не принимается из тела запроса, чтобы нельзя было создать
        бронь от чужого имени.
        """
        booking = serializer.save(guest=self.request.user)
        logger.info(f'Booking {booking.id} created by {self.request.user.username} for listing {booking.listing.id}')


class BookingDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or cancel a single booking.

    Editing is intentionally not supported — a booking is either
    cancelled and re-created, or left as-is; see project notes on why
    partial updates to dates/price were deliberately left out.

    Просмотр или отмена одной брони.

    Редактирование сознательно не поддерживается — бронь либо
    отменяется и создаётся заново, либо остаётся как есть; см. решение
    в переписке о том, почему частичное изменение дат/цены не
    реализовано намеренно.
    """
    serializer_class = BookingListSerializer
    permission_classes = [IsBookingParticipant]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).select_related('listing', 'guest')

    def perform_destroy(self, instance):
        """
        Prevent cancelling bookings that have already ended, and
        surface a clean error instead of a raw ProtectedError when
        the booking already has a review attached.

        Запрещает отмену уже завершённых броней и возвращает понятную
        ошибку вместо голого ProtectedError, если у брони уже есть
        привязанный отзыв.
        """
        if instance.end_date < timezone.now():
            raise DRFValidationError("Can't cancel a booking that has already ended.")
        try:
            instance.delete()
        except ProtectedError:
            raise DRFValidationError("Can't cancel a booking that already has a review.")


class ListingBookedDatesView(APIView):
    """
    Public endpoint returning the date ranges already booked (and paid)
    for a listing, used to disable those dates in the frontend calendar.

    Only paid bookings count as occupying dates — a pending, unpaid
    booking does not block the calendar for other guests.

    Публичный эндпоинт, отдающий диапазоны дат, уже занятых (и
    оплаченных) для листинга — используется для блокировки этих дат
    в календаре на фронтенде.

    Занятыми считаются только оплаченные брони — неоплаченная (pending)
    бронь не блокирует календарь для других гостей.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, listing_id):
        bookings = Booking.objects.filter(
            listing_id=listing_id, status=BookingStatusChoices.paid
        ).values('start_date', 'end_date')
        booked_ranges = [
            {'from': b['start_date'].date(), 'to': b['end_date'].date()}
            for b in bookings
        ]
        return Response(booked_ranges)



#-----------------------------------------------------------------------------------------------------------------------


class BookingPaymentView(generics.GenericAPIView):
    """
    Simulates paying for a pending booking with a card.

    Validates the submitted card details (format only — this is not
    a real payment gateway), stores only the last 4 digits of the
    card, marks the booking as paid, and sends a confirmation email.

    Симулирует оплату ожидающей брони картой.

    Проверяет введённые данные карты (только формат — это не
    интеграция с реальным платёжным шлюзом), сохраняет только
    последние 4 цифры карты, помечает бронь оплаченной и отправляет
    письмо-подтверждение.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        Look up the booking by id, scoped to the requesting user as
        guest, so a user cannot pay for (or probe the existence of)
        someone else's booking.

        Ищет бронь по id, ограничиваясь текущим пользователем как
        гостем — чтобы нельзя было оплатить (или проверить
        существование) чужой брони.
        """
        booking = get_object_or_404(Booking, pk=pk, guest=request.user)

        if booking.status != BookingStatusChoices.pending:
            return Response({'detail': 'This booking is not pending payment.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_number = serializer.validated_data['card_number']
        booking.card_last4 = card_number[-4:]
        booking.status = BookingStatusChoices.paid
        booking.save(update_fields=['card_last4', 'status'])

        send_mail(
            subject='Booking payment confirmed',
            message=f'Your booking for {booking.listing.apartment_name} has been paid. Amount: {booking.price} €.',
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=True,
        )

        return Response({
            'status': 'paid',
            'message': 'Payment successful. A confirmation has been sent to your email.',
            'card_last4': booking.card_last4,
        })