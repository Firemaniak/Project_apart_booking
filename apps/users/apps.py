from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'   # ← явно фиксируем label, чтобы AUTH_USER_MODEL = 'users.User' совпал
