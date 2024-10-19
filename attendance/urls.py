from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    # URL to access the give-attendance.html template
    path('give-attendance/', views.give_attendance_view, name='give_attendance_view'),
]
