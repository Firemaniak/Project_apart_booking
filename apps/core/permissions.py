from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):

    """Only the object's owner can edit or delete it; everyone can read it.
    Редактировать/удалять может только владелец объекта; читать — все."""

    owner_field = 'owner'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, self.owner_field) == request.user


class IsBookingParticipant(BasePermission):

    """
    The booking can be viewed by the guest and the listing owner (listing.owner).
    Only the guest can delete (cancel) the booking.
    Видеть бронь могут: сам гость (guest) и хозяин листинга (listing.owner).
    Удалять (отменять) бронь может только гость.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.guest == request.user or obj.listing.owner == request.user
        return obj.guest == request.user