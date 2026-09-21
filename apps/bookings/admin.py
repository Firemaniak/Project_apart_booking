from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(SimpleHistoryAdmin):
    list_display = ['guest', 'listing', 'start_date', 'end_date', 'price', 'payment_type']
    list_filter = ['payment_type']
    readonly_fields = ['price']