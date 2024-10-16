from django.contrib import admin
from .models import Employee,EmployeeDocument, Device, AttendanceLog, Shift,TemporaryShift, Schedule, WorkHours
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from .views import schedule_report_view  # Custom view import করুন

class EmployeeDocumentInline(admin.TabularInline):
    """
    Inline admin for EmployeeDocument model to display documents related to an employee.
    """
    model = EmployeeDocument
    extra = 1  # Number of empty forms to display for adding new documents
    fields = ('document_name', 'document_type', 'document_file')
    readonly_fields = ('upload_date',)  # Make upload_date read-only in the inline form

# Registering Employee model in the admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee model.
    """
    list_display = ('id', 'employee_id', 'company', 'department', 'position', 'contact_number', 'date_of_joining', 'first_name')
    search_fields = ('employee_id', 'department', 'position', 'company__name')
    list_filter = ('department', 'position', 'date_of_joining', 'company')
    
    # Exclude the company field from the form
    exclude = ('company',)  
    
    inlines = [EmployeeDocumentInline]  # Add the inline to the Employee admin
    # Define fieldsets for the admin form
    fieldsets = (
        (None, {  # First fieldset with no title
            'fields': ('employee_id', 'first_name', 'last_name',  'contact_number', 'date_of_joining')
        }),
        ('Details', {  # Second fieldset with a title
            'fields': ('department', 'position', 'gender', 'bloodGroup', 'religion', 'maritalStatus', 'date_of_birth', 'email')
        }),

    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান

    def save_model(self, request, obj, form, change):
        if not obj.company:  
            obj.company = request.user.company 
        super().save_model(request, obj, form, change)

    def get_formset(self, request, obj=None, **kwargs):
        # Get the formset for the inline model
        formset = super().get_formset(request, obj, **kwargs)

        # Update the widget for the 'document_file' field in the inline formset
        for form in formset.forms:
            form.fields['document_file'].widget.attrs.update({'class': 'custom-file-input'})  # Custom CSS class for file input

        return formset
# Registering Device model in the admin
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Admin interface for Device model.
    """
    list_display = ('id', 'device_id', 'location', 'company', 'ip_address', 'port','last_sync_time', )  # Added 'company' and 'is_synced'
    search_fields = ('device_id', 'location', 'ip_address', 'company__name')  # Added search by company name
    list_filter = ('location', 'company', 'last_sync_time')  # Added filter by 'company'
    ordering = ('-last_sync_time',)  # Devices ordered by latest sync time
    list_editable = ('device_id','location', 'ip_address','port')  # Allow inline editing of location and IP address
    readonly_fields = ('last_sync_time',)  # Prevent editing of sync time



    exclude = ('company',)  
    def save_model(self, request, obj, form, change):
        if change:
            obj.company = request.user.company  # Set the company to the logged-in user's company
        super().save_model(request, obj, form, change)  


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান

    # Define fieldsets for the admin form
    fieldsets = (
        ("Device Information", {  # First fieldset with no title
            'fields': ('device_id', 'location', 'ip_address', 'port')
        }),
        ('Advanced Settings', {  # Second fieldset with a title
            'fields': ('last_sync_time',),  # You can add more fields as needed
            'classes': ('collapse',),  # This will make this fieldset collapsible
        }),
    )

# Registering AttendanceLog model in the admin
@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AttendanceLog model.
    """
    list_display = ('id', 'employee', 'company', 'punch_datetime', 'in_out_status', 'punch_mode', 'device', 'locationName')
    search_fields = ('employee__username', 'company__name', 'device__device_id', 'in_out_status')
    list_filter = ('company', 'in_out_status', 'punch_mode', 'punch_datetime')

    exclude = ('company',)  
    def save_model(self, request, obj, form, change):
        if change:
            obj.company = request.user.company  # Set the company to the logged-in user's company
        super().save_model(request, obj, form, change) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান

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
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান
    
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Override the formfield for foreign keys to filter by company."""
        if db_field.name == "employee":
            # Filter employees by the user's company
            kwargs["queryset"] = Employee.objects.filter(company=request.user.company)
        elif db_field.name == "shift":
            # Filter shifts by the user's company if applicable
            kwargs["queryset"] = Shift.objects.filter(company=request.user.company)  # Adjust based on your Shift model's field
        return super().formfield_for_foreignkey(db_field, request, **kwargs)       


    # Custom URL and view
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('schedule-report/', self.admin_site.admin_view(schedule_report_view), name='schedule_report'),  # Custom view URL
        ]
        return custom_urls + urls

    # Custom action button to access the custom view
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['schedule_report_url'] = reverse('admin:schedule_report')
        return super().changelist_view(request, extra_context=extra_context)

    # Add link in the admin panel
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['employee'].help_text = format_html(
            '<a href="{}">View Schedule Report</a>',
            reverse('admin:schedule_report')  # Link to custom view
        )
        return super().render_change_form(request, context, *args, **kwargs)         
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # সুপারইউজার হলে সব ডিভাইস দেখান
        return qs.filter(company=request.user.company)  # অন্য ব্যবহারকারীর জন্য শুধুমাত্র তাদের কোম্পানির ডিভাইস দেখান
            