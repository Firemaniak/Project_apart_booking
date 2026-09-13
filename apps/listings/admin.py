from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(SimpleHistoryAdmin):
    list_display = ['apartment_name', 'country', 'price_per_night', 'owner']
    list_filter = ['country', 'parking', 'wifi']
    search_fields = ['apartment_name', 'address']
