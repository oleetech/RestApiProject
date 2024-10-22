from django.contrib import admin
from .models import Employee,EmployeeDocument, Device, AttendanceLog, Shift,TemporaryShift, Schedule, WorkHours
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from .views import schedule_report_view  # Custom view import করুন
from django.core.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from django.contrib import messages

class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 1 
    fields = ('document_name', 'document_type', 'document_file')
    readonly_fields = ('upload_date',)  

from .forms import EmployeeForm

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeForm  # Use the custom form
    inlines = [EmployeeDocumentInline]  
 
    def get_form(self, request, obj=None, **kwargs):
        # Get the form class by calling super
        form = super().get_form(request, obj, **kwargs)
        
        # Define a wrapper function that injects the request into the form instance
        class RequestForm(form):
            def __init__(self2, *args, **inner_kwargs):
                # Pass the request object to the form
                inner_kwargs['request'] = request
                super().__init__(*args, **inner_kwargs)

        # Return the modified form class that includes the request
        return RequestForm

    # Admin configurations (e.g., list_display, search_fields, etc.)
    list_display = ('id', 'employee_id', 'company', 'department', 'position', 'contact_number', 'date_of_joining', 'name')
    search_fields = ('employee_id', 'department__name', 'position', 'company__name')
    list_filter = ('department', 'position', 'date_of_joining', 'company')
    exclude = ('company',)

    fieldsets = (
        ("Company Information ", {
            'fields': ('employee_id', 'user', 'name', 'contact_number', 'date_of_joining')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'marital_status', 'blood_group', 'religion', 'email')
        }),
        ('Employment Details', {
            'fields': ('department', 'position', 'status', 'salary_type', 'salary_amount')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_ifsc_code')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('References', {
            'fields': ('reference_name', 'reference_phone')
        }),
        ('Address', {
            'fields': ('local_address', 'permanent_address')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
        if not obj.company:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if request.POST:
            for form in formset:
                # Custom validation logic
                if not form.cleaned_data.get('document_file'):
                    form.add_error('document_file', 'Document file is required.')
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
        if not obj.company:  
            if not request.user.company:
                raise ValidationError("আপনার ইউজার প্রোফাইলে কোম্পানি সেট করা নেই। অনুগ্রহ করে কোম্পানি সিলেক্ট করুন।")
            obj.company = request.user.company 
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
    exclude = ('company',)  # Hide company field in the form

    def save_model(self, request, obj, form, change):
        # Check if the object has a company
        if not obj.company:
            # Check if the user has a company
            if not hasattr(request.user, 'company') or not request.user.company:
                form.add_error(None, "আপনার ইউজার প্রোফাইলে কোম্পানি সেট করা নেই। অনুগ্রহ করে কোম্পানি সিলেক্ট করুন।")
                raise ValidationError("Company must be set for the user.")
            # Assign the user's company to the Holiday object
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Show all holidays for superuser
        return qs.filter(company=request.user.company) 
    
from .models import Department, Notice

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name', 'company__name')
    list_filter = ('company',)

    def get_exclude(self, request, obj=None):
        # Exclude the 'company' field for non-superusers
        if not request.user.is_superuser:
            return ('company',)
        return super().get_exclude(request, obj=obj)  # No exclusions for superusers

    def save_model(self, request, obj, form, change):
        # Check if the user is not a superuser
        if not request.user.is_superuser:
            # Check if the department object has a company
            if not obj.company_id:
                # Check if the user has a company
                if not hasattr(request.user, 'company') or not request.user.company:
                    form.add_error(None, "আপনার ইউজার প্রোফাইলে কোম্পানি সেট করা নেই। অনুগ্রহ করে কোম্পানি সিলেক্ট করুন।")
                    raise ValidationError("User profile must have an associated company.")
                
                # Assign the user's company to the department
                obj.company = request.user.company
        
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Optionally limit the queryset to only departments in the user's company
        qs = super().get_queryset(request)
        if hasattr(request.user, 'company') and request.user.company:
            return qs.filter(company=request.user.company)
        return qs
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_departments', 'created_at')
    search_fields = ('title', 'content', 'company__name', 'department__name')
    list_filter = ('department', 'created_at')
    # readonly_fields = ('created_at',)
    exclude = ('company','created_at', )
    
    class Media:
        js = ('attendance/js/custom_notice_admin.js',)
        
    def get_departments(self, obj):
        # Join department names to display as a string
        return ", ".join([dept.name for dept in obj.department.all()])

    get_departments.short_description = 'Departments'

    def get_queryset(self, request):
        # Optionally limit the queryset to only departments in the user's company
        qs = super().get_queryset(request)
        if hasattr(request.user, 'company') and request.user.company:
            return qs.filter(company=request.user.company)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        # Get the form
        form = super().get_form(request, obj, **kwargs)

        # Filter the user and department fields based on the request user's company
        if request.user.is_authenticated and hasattr(request.user, 'company'):
            company_id = request.user.company_id  # Get the company ID

            # Check if the 'user' field exists before applying the filter
            if 'user' in form.base_fields:
                form.base_fields['user'].queryset = get_user_model().objects.filter(company_id=company_id)
            
            # Check if the 'department' field exists before applying the filter
            if 'department' in form.base_fields:
                form.base_fields['department'].queryset = Department.objects.filter(company_id=company_id)

        return form

    def get_fields(self, request, obj=None):
        # Get the base fields
        fields = super().get_fields(request, obj)

        # Customize field visibility based on the target_type value
        if obj and obj.target_type == 'ALL':
            fields.remove('department')
            fields.remove('user')
        elif obj and obj.target_type == 'DEPT':
            fields.remove('user')
        elif obj and obj.target_type == 'USER':
            fields.remove('department')

        return fields
    
    def save_model(self, request, obj, form, change):
        # Check if the user is not a superuser
        if not request.user.is_superuser:
            # Check if the department object has a company
            if not obj.company_id:
                # Check if the user has a company
                if not hasattr(request.user, 'company') or not request.user.company:
                    form.add_error(None, "আপনার ইউজার প্রোফাইলে কোম্পানি সেট করা নেই। অনুগ্রহ করে কোম্পানি সিলেক্ট করুন।")
                    raise ValidationError("User profile must have an associated company.")
                
                # Assign the user's company to the department
                obj.company = request.user.company
        
        super().save_model(request, obj, form, change)