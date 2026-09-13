from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']
    ordering = ['username']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional info', {
            'fields': ('birth_date', 'bio', 'address', 'phone', 'avatar')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional info', {
            'fields': ('email', 'birth_date', 'phone')
        }),
    )

    actions = ['deactivate_users']

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    @admin.action(description='Деактивировать выбранных юзеров')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
