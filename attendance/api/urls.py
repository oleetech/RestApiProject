from django.urls import path, include
from rest_framework.routers import DefaultRouter


# Import EmployeeViewSet from employee_views.py
from .views.employee_views import EmployeeViewSet

# Import DeviceViewSet from device_views.py
from .views.device_views import DeviceViewSet

# Import AttendanceLogViewSet from attendance_log_views.py
from .views.attendance_log_views import AttendanceLogViewSet

# Import ShiftViewSet from shift_views.py
from .views.shift_views import ShiftViewSet

# Import ScheduleViewSet from schedule_views.py
from .views.schedule_views import ScheduleViewSet

# Import WorkHoursViewSet from workhours_views.py
from .views.workhours_views import WorkHoursViewSet




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
