from django.contrib import admin
from .models import Employee, Device, AttendanceLog, Shift,TemporaryShift, Schedule, WorkHours

# Registering Employee model in the admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee model.
    """
    list_display = ('id', 'employee_id', 'company', 'department', 'position', 'contact_number', 'date_of_joining','first_name')
    search_fields = ('employee_id', 'department', 'position', 'company__name')
    list_filter = ('department', 'position', 'date_of_joining', 'company')

    # ফর্ম থেকে company ফিল্ড হাইড করার জন্য exclude ব্যবহার করা হচ্ছে
    exclude = ('company',)  # company ফিল্ডটি ফর্মে দেখানো হবে না

    def save_model(self, request, obj, form, change):

        if  change:  
            obj.company = request.user.company  # লগইনকৃত ইউজারের কোম্পানি ডিফল্টভাবে সেট করা হচ্ছে
        super().save_model(request, obj, form, change)     
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
    list_display = ('id', 'employee', 'company', 'punch_datetime', 'in_out_status', 'punch_mode', 'device', 'locationName')
    search_fields = ('employee__username', 'company__name', 'device__device_id', 'in_out_status')
    list_filter = ('company', 'in_out_status', 'punch_mode', 'punch_datetime')


# Registering Shift model in the admin
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """
    Admin interface for Shift model.
    """

    # Fields to display in the list view
    list_display = ('id', 'name', 'company', 'start_time', 'end_time', 'break_duration', 'status',)
    
    # Fields to search
    search_fields = ('name', 'company__name')  # Allows searching by company name

    # Fields to filter by
    list_filter = ('status', 'start_time', 'end_time', 'company')  # Added filtering by company and status




    # Optionally, you can define how many entries are displayed per page
    list_per_page = 20  # Adjust this number as needed

    # Optional: Add actions
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        """
        Custom action to mark selected shifts as active.
        """
        queryset.update(status='ACTIVE')
        self.message_user(request, "Selected shifts marked as active.")

    mark_active.short_description = "Mark selected shifts as active"

    def mark_inactive(self, request, queryset):
        """
        Custom action to mark selected shifts as inactive.
        """
        queryset.update(status='INACTIVE')
        self.message_user(request, "Selected shifts marked as inactive.")

    mark_inactive.short_description = "Mark selected shifts as inactive"
    # ফর্ম থেকে company ফিল্ড হাইড করার জন্য exclude ব্যবহার করা হচ্ছে
    exclude = ('company',)  # company ফিল্ডটি ফর্মে দেখানো হবে না

    def save_model(self, request, obj, form, change):

        if  change:  
            obj.company = request.user.company  # লগইনকৃত ইউজারের কোম্পানি ডিফল্টভাবে সেট করা হচ্ছে
        super().save_model(request, obj, form, change)
    
from .models import Workday

@admin.register(Workday)
class WorkdayAdmin(admin.ModelAdmin):
    """
    Admin interface for the Workday model.
    """
    list_display = ('id', 'day')  # Display the ID and the day in the list view
    search_fields = ('day',)  # Allow searching by day
    list_filter = ('day',)  # Allow filtering by day

    # Optional: Set the number of entries per page
    list_per_page = 20  # Adjust based on preference

    # Optional: Add ordering by day
    ordering = ['day']  # Orders the list by the day (e.g., MON, TUE)

    # Optional: Customize the form layout (if needed)
    fieldsets = (
        (None, {
            'fields': ('day',),  # Only display the day field in the form
        }),
    )

    # Optional: Disable adding and deleting entries from the admin (if needed)
    def has_add_permission(self, request):
        # Uncomment the line below to prevent adding new workdays
        # return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Uncomment the line below to prevent deleting workdays
        # return False
        return super().has_delete_permission(request, obj)

# Registering Schedule model in the admin
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'employee_display', 'shift', 'workday_display')

    # Fields to search
    search_fields = ('employee__employee_id', 'employee__position', 'shift__name', 'workdays')

    # Fields to filter by
    list_filter = ('shift', 'workdays')

    def workday_display(self, obj):
        """
        Display all selected workdays as a comma-separated string.
        """
        return ', '.join([day.day for day in obj.workdays.all()])  # Workdays display

    def employee_display(self, obj):
        """
        Display employee details in the admin panel.
        """
        return f"{obj.employee.employee_id} - {obj.employee.position}"  # Employee ID and position

    employee_display.short_description = 'Employee'

    # ফর্ম থেকে company ফিল্ড হাইড করার জন্য exclude ব্যবহার করা হচ্ছে
    exclude = ('company',)  # company ফিল্ডটি ফর্মে দেখানো হবে না

    def save_model(self, request, obj, form, change):

        if  change:  
            obj.company = request.user.company  # লগইনকৃত ইউজারের কোম্পানি ডিফল্টভাবে সেট করা হচ্ছে
        super().save_model(request, obj, form, change)    
# Registering WorkHours model in the admin
@admin.register(WorkHours)
class WorkHoursAdmin(admin.ModelAdmin):
    """
    Admin interface for WorkHours model.
    """
    list_display = ('id', 'employee','company', 'date', 'total_hours', 'overtime_hours')
    search_fields = ('employee__user__username', 'date')
    list_filter = ('date',)
    # ফর্ম থেকে company ফিল্ড হাইড করার জন্য exclude ব্যবহার করা হচ্ছে
    exclude = ('company',)  # company ফিল্ডটি ফর্মে দেখানো হবে না

    def save_model(self, request, obj, form, change):

        if  change:  
            obj.company = request.user.company  # লগইনকৃত ইউজারের কোম্পানি ডিফল্টভাবে সেট করা হচ্ছে
        super().save_model(request, obj, form, change)
from .models import Holiday

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """
    Holiday মডেলের জন্য অ্যাডমিন ইন্টারফেস।
    """
    list_display = ('company', 'date', 'reason')
    search_fields = ('company__name', 'reason')
    list_filter = ('company', 'date')

    # ফর্ম থেকে company ফিল্ড হাইড করার জন্য exclude ব্যবহার করা হচ্ছে
    exclude = ('company',)  # company ফিল্ডটি ফর্মে দেখানো হবে না

    def save_model(self, request, obj, form, change):

        if  change:  
            obj.company = request.user.company  # লগইনকৃত ইউজারের কোম্পানি ডিফল্টভাবে সেট করা হচ্ছে
        super().save_model(request, obj, form, change)