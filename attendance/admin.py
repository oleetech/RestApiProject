from django.contrib import admin
from .models import Attendance, AttendanceLog

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin interface for Attendance model.
    """
    list_display = ('id', 'user', 'company', 'date', 'status')  # Adjust the fields to display as needed
    search_fields = ('user__username', 'company__name', 'date')  # Fields to search
    list_filter = ('company', 'date', 'status')  # Filters to apply in the admin panel

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AttendanceLog model.
    """
    list_display = ('id', 'attendance', 'log_time', 'action')  # Adjust the fields to display as needed
    search_fields = ('attendance__user__username', 'attendance__company__name', 'log_time')  # Fields to search
    list_filter = ('attendance__company', 'action', 'log_time')  # Filters to apply in the admin panel
