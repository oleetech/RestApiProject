from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)  # Registering the viewset

urlpatterns = [
    path('', include(router.urls)),  # Including all router-generated URLs
]
