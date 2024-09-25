"""
URL configuration for RestApiProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

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
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('djoser.urls')),  # Djoser URL
    re_path(r'^auth/', include('djoser.urls.jwt')),  # Djoser JWT URL
    re_path(r'^auth/', include('social_django.urls', namespace='social')),  # Social Auth URL
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger
    path('auth-api/', include('authentication.api.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
