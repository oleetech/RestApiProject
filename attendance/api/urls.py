from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, 
    DeviceViewSet, 
    AttendanceLogViewSet, 
    ShiftViewSet, 
    ScheduleViewSet, 
    WorkHoursViewSet
)

# Initialize the DefaultRouter
router = DefaultRouter()

# Register the routes for each viewset
router.register(r'employees', EmployeeViewSet)
router.register(r'devices', DeviceViewSet)
router.register(r'attendance-logs', AttendanceLogViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'work-hours', WorkHoursViewSet)

# Include all the router URLs
urlpatterns = [
    path('', include(router.urls)),
]
