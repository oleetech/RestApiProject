
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.i18n import i18n_patterns

# Swagger API ডকুমেন্টেশন সেটআপ
schema_view = get_schema_view(
   openapi.Info(
      title="Accounting Finance API",
      default_version='v1',
      description="How To Use API",
      terms_of_service="https://www.kreatech.ca/terms/",
      contact=openapi.Contact(email="rebelsoft111122@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('', include('admin_soft.urls')),

    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('djoser.urls')),  # Djoser URL
    re_path(r'^auth/', include('djoser.urls.jwt')),  # Djoser JWT URL
    re_path(r'^auth/', include('social_django.urls', namespace='social')),  # Social Auth URL
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger
    re_path('^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('auth-api/', include('authentication.api.urls')),
    path('attendance-api/', include('attendance.api.urls')),
    path('set_language/', include('django.conf.urls.i18n')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
