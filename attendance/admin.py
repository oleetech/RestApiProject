from django.contrib import admin
from .models import Employee, Device, AttendanceLog, Shift, Schedule, WorkHours

# Registering Employee model in the admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee model.
    """
    list_display = ('id', 'user', 'employee_id', 'department', 'position', 'contact_number', 'date_of_joining')
    search_fields = ('user__username', 'employee_id', 'department', 'position')
    list_filter = ('department', 'position', 'date_of_joining')

# Registering Device model in the admin
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Admin interface for Device model.
    """
    list_display = ('id', 'device_id', 'location', 'company', 'ip_address', 'last_sync_time', 'is_synced')  # Added 'company' and 'is_synced'
    search_fields = ('device_id', 'location', 'ip_address', 'company__name')  # Added search by company name
    list_filter = ('location', 'company', 'last_sync_time')  # Added filter by 'company'
    ordering = ('-last_sync_time',)  # Devices ordered by latest sync time
    list_editable = ('location', 'ip_address')  # Allow inline editing of location and IP address
    readonly_fields = ('last_sync_time',)  # Prevent editing of sync time

    def is_synced(self, obj):
        """
        Show whether the device has been synced within the last 24 hours.
        """
        return obj.is_synced
    is_synced.boolean = True  # Display as a boolean icon in the list display
    is_synced.short_description = 'Synced Recently'

    def save_model(self, request, obj, form, change):
        """
        Custom logic when saving a device through the admin interface.
        """
        # Add any additional custom actions when saving the device
        super().save_model(request, obj, form, change)

# Registering AttendanceLog model in the admin
@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AttendanceLog model.
    """
    list_display = ('id', 'employee', 'company', 'timestamp', 'status', 'mode', 'device', 'locationName')
    search_fields = ('employee__username', 'company__name', 'device__device_id', 'status')
    list_filter = ('company', 'status', 'mode', 'timestamp')


# Registering Shift model in the admin
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """
    Admin interface for Shift model.
    """
    list_display = ('id', 'name', 'start_time', 'end_time', 'break_duration')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')

# Registering Schedule model in the admin
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for Schedule model.
    """
    list_display = ('id', 'employee', 'shift', 'workday')
    search_fields = ('employee__user__username', 'shift__name', 'workday')
    list_filter = ('shift', 'workday')

# Registering WorkHours model in the admin
@admin.register(WorkHours)
class WorkHoursAdmin(admin.ModelAdmin):
    """
    Admin interface for WorkHours model.
    """
    list_display = ('id', 'employee', 'date', 'total_hours', 'overtime_hours')
    search_fields = ('employee__user__username', 'date')
    list_filter = ('date',)
