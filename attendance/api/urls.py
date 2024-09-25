from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, AttendanceLogViewSet

router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet)
router.register(r'attendance-logs', AttendanceLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
