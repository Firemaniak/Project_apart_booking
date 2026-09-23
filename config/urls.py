from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

BASE_DIR = settings.BASE_DIR

schema_view = get_schema_view(
    openapi.Info(title="Apartment Booking API", default_version='v1'),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/listings/', include('apps.listings.urls')),
    path('api/bookings/', include('apps.bookings.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/statistics/', include('apps.statist.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]


urlpatterns += [
    path(f'{settings.MEDIA_URL.lstrip("/")}<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]


FRONTEND_DIR = BASE_DIR / 'frontend'

urlpatterns += [
    path('', serve, {'document_root': FRONTEND_DIR, 'path': 'index.html'}),
    path('<path:path>', serve, {'document_root': FRONTEND_DIR}),
]