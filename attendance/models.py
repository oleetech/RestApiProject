from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company 
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField  # Use CKEditor 5 field
import os

class Department(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')

    class Meta:
        unique_together = ('name', 'company')  # Ensures each department name is unique within a company

    def __str__(self):
        return f"{self.name} - {self.company.name}"



class Employee(models.Model):

    # Gender Choices
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    # Blood Group Choices
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    # Religion Choices
    RELIGION_CHOICES = [
        ('Christianity', 'Christianity'),
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Buddhism', 'Buddhism'),
        ('Sikhism', 'Sikhism'),
        ('Judaism', 'Judaism'),
        ('Other', 'Other'),
    ]

    # Marital Status Choices
    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]

    # Status Choices
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
        ('Suspended', 'Suspended'),
        ('Terminated', 'Terminated'),
        ('Resigned', 'Resigned'),
    ]

    # Salary Type Choices
    SALARY_TYPE_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Hourly', 'Hourly'),
        ('Contract', 'Contract'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_employees',
        verbose_name=_("Company"),
        null=True, blank=True,
    )
    
    user = models.ForeignKey(
        get_user_model(),  
        on_delete=models.CASCADE, 
        related_name='employees',  
        null=True,  
        blank=True  
    )  

    employee_id = models.CharField(
        max_length=20,
        verbose_name=_("Employee ID"),
    )

    name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_(" Name"))
    father_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Father's Name"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    contact_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("Contact Number"))  

    # Address Fields
    local_address = models.TextField(null=True, blank=True, verbose_name=_("Local Address"))
    permanent_address = models.TextField(null=True, blank=True, verbose_name=_("Permanent Address"))

    # Reference Fields
    reference_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Reference Name"))
    reference_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("Reference Phone"))

    # Employment Fields
    designation = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Designation"))
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='Active', 
        verbose_name=_("Status")
    )

    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, verbose_name=_("Salary Type"))
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Salary Amount"))

    # Bank Account Details
    bank_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Bank Name"))
    bank_account_number = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Bank Account Number"))
    bank_ifsc_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Bank IFSC Code"))

    # Other Personal Details
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, blank=True, null=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    date_of_joining = models.DateField(null=True, blank=True, verbose_name=_("Date of Joining"))
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_("Email Address"))

    # Emergency Contact Fields
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Emergency Contact Name"))
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("Emergency Contact Phone"))
    emergency_contact_relationship = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Emergency Contact Relationship"))

    # Department and Position
    department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Department"))  
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Position Title"))  

    class Meta:
        verbose_name = _("Employee")  
        verbose_name_plural = _("Employees")  
        ordering = ['date_of_joining']  
        constraints = [
            models.UniqueConstraint(fields=['company', 'employee_id'], name='unique_employee_per_company'),
            models.UniqueConstraint(fields=['contact_number'], name='unique_contact_number'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
            models.CheckConstraint(check=models.Q(date_of_birth__lt=models.F('date_of_joining')), name='check_birth_before_joining'),
            models.CheckConstraint(check=models.Q(employee_id__regex=r'^[a-zA-Z0-9]+$'), name='check_employee_id_alphanumeric'),
            models.CheckConstraint(check=models.Q(contact_number__regex=r'^[0-9]+$'), name='check_contact_number_numeric'),
            models.CheckConstraint(check=models.Q(email__contains='@'), name='check_valid_email'),
            models.CheckConstraint(check=models.Q(date_of_birth__gt='1900-01-01'), name='check_valid_birth_date'),
        ]

    def save(self, *args, **kwargs):
        # Your custom save logic here
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if not self.name and not self.father_name:
            raise ValidationError(_("At least one of First Name or Father's Name must be provided."))

        if self.email and '@' not in self.email:
            raise ValidationError(_("Email address must contain a valid '@' symbol."))

        if self.contact_number and not self.contact_number.isdigit():
            self.add_error('contact_number', _("Contact number must be numeric."))

        if self.contact_number and (len(self.contact_number) < 10 or len(self.contact_number) > 15):
            self.add_error('contact_number', _("Contact number must be between 10 and 15 digits."))

    def __str__(self):
        return f"({self.employee_id} {self.name})"

class EmployeeDocument(models.Model):
    EMPLOYEE_DOCUMENT_TYPES = (
        ('Resume', 'Resume'),
        ('Contract', 'Contract'),
        ('ID Card', 'ID Card'),
        ('Other', 'Other'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True, blank=True,default=None)  
    document_name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=20, choices=EMPLOYEE_DOCUMENT_TYPES)
    upload_date = models.DateTimeField(auto_now_add=True)
    document_file = models.FileField(upload_to='employee_documents/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'png'])])
 
    class Meta:
        verbose_name = _("Employee Document")
        verbose_name_plural = _("Employee Documents")
        ordering = ['upload_date']  # Default ordering by upload date
        
    def clean(self):
        super().clean()
        # File size validation (e.g., 5MB)
        if self.document_file.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError(_("File size should not exceed 5MB. Your file is %s") % filesizeformat(self.document_file.size))


class Device(models.Model):
    device_id = models.CharField(max_length=50, unique=True)  
    location = models.CharField(max_length=100)  
    description = models.CharField(max_length=255,null=True, blank=True)  
    ip_address = models.GenericIPAddressField(null=True, blank=True)  
    last_sync_time = models.DateTimeField(null=True, blank=True)  
    serial_number = models.CharField(max_length=255, unique=True,null=True)  
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)  
    port = models.IntegerField(default=4370)  # মেশিনের পোর্ট

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ['-last_sync_time']  # Order devices by last sync time (latest first)
        constraints = [
            models.CheckConstraint(check=models.Q(port__gte=1, port__lte=65535), name='check_valid_port_range'),
            models.UniqueConstraint(fields=['company', 'ip_address'], name='unique_ip_per_company')
        ]
    def __str__(self):
        """
        Return a string representation of the device showing its ID and location.
        """
        return f"{self.device_id} - {self.location}"

    def clean(self):
        super().clean()
        # if len(self.serial_number) < 10:
        #     raise ValidationError("Serial number must be at least 10 characters long.")
        if not self.ip_address:
            raise ValidationError("Device must have a valid IP address.")
        if not (1 <= self.port <= 65535):
            raise ValidationError(_("Port number must be between 1 and 65535."))
    @property
    def is_synced(self):
        """
        Check if the device has been synced in the last 24 hours.
        """


        if self.last_sync_time:
            return timezone.now() - self.last_sync_time < timedelta(days=1)
        return False

    def get_device_summary(self):
        """
        Return a summary of the device, including ID, location, and company.
        """
        return f"Device {self.device_id} located at {self.location}, owned by {self.company.name}."




        
class AttendanceLog(models.Model):
    
    """
    ব্যবহারকারীর চেক ইন এবং চেক আউট তথ্য সংরক্ষণ করার জন্য উপস্থিতি লগ মডেল।
    """
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True, blank=True,default=None)  
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_logs',null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True)
    punch_datetime = models.DateTimeField(default=timezone.now, verbose_name=_("Date & Time of Punch"))
   
    STATUS_CHOICES = [
        ('IN', 'Check-In'),
        ('OUT', 'Check-Out'),
        ('BREAK_IN', 'Break-In'),
        ('BREAK_OUT', 'Break-Out'),
    ]
    in_out_status = models.CharField(max_length=20, choices=STATUS_CHOICES,     default='IN', verbose_name=_("In/Out Status"))
    VERIFICATION_CHOICES = [
        ('FP', 'Fingerprint'),
        ('FACE', 'Face'),
        ('CARD', 'Card'),
        ('PWD', 'Password'),
        ('GPS', 'GPS'),
        ('MANUAL', 'Manual'),
    ]
    verification_method = models.CharField(
        max_length=10,
        choices=VERIFICATION_CHOICES,
        default='FP',
        verbose_name=_("Verification Method")
    )

    punch_mode = models.CharField(
        max_length=10,
        choices=[('AUTO', 'Auto'), ('MANUAL', 'Manual')],
        default='AUTO',
        verbose_name=_("Punch Mode")
    )
    work_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_("Work Code")
    )
    sync = models.BooleanField(default=False)

    locationName = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.username} - {self.timestamp} - {self.status}"

    class Meta:
        verbose_name = "Attendance Log"
        verbose_name_plural = "Attendance Logs"
        ordering = ['-punch_datetime']  # Order by latest timestamp first
        constraints = [
            models.UniqueConstraint(fields=['employee', 'punch_datetime'], name='unique_attendance_log_per_user_per_day_per_checkin')
        ]

    def clean(self):
        """
        Custom validation to ensure attendance log has valid latitude and longitude if provided.
        """
        if (self.latitude is not None) != (self.longitude is not None):
            raise ValidationError("Both latitude and longitude must be provided together.")

    @property
    def is_recent(self):
        """
        Check if the attendance log was created within the last 24 hours.
        """
        return timezone.now() - self.timestamp < timedelta(days=1)

    def get_attendance_summary(self):
        """
        Return a summary of the attendance log, including employee name, status, and location.
        """
        location = self.locationName if self.locationName else 'Unknown Location'
        return f"Attendance Log: {self.employee.username} {self.status} at {location} on {self.timestamp}."



class Shift(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]    
    name = models.CharField(max_length=50)  # Name of the shift
    start_time = models.TimeField()  # Shift start time
    end_time = models.TimeField()  # Shift end time
    break_duration = models.DurationField(null=True, blank=True)  # Optional break duration
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shifts',null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')  # Shift status
    class Meta:
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"
        ordering = ['start_time']  # Order shifts by start time
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='unique_shift_per_company')  # Unique constraint
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name}) - Status: {self.status}"  # Return shift details

    @property
    def duration(self):
        """
        Calculate the duration of the shift considering break time.
        If start_time or end_time is None, return None.
        """
        # Check if both start_time and end_time are not None
        if self.start_time and self.end_time:
            shift_start = timezone.datetime.combine(timezone.now().date(), self.start_time)
            shift_end = timezone.datetime.combine(timezone.now().date(), self.end_time)
            shift_duration = shift_end - shift_start

            if self.break_duration:
                shift_duration -= self.break_duration  # Subtract break duration

            return shift_duration

        return None  # Return None if start_time or end_time is None

    def clean(self):
        """
        Custom validation to ensure that the end time is after the start time.
        """
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def is_active(self):
        """
        Check if the shift is currently active based on the status.
        """
        return self.status == 'ACTIVE'

class Workday(models.Model):
    day = models.CharField(max_length=10, choices=[
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ])

    def __str__(self):
        return self.day

class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,default=None,blank=True,null=True)  
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE,blank=True,null=True,default=None)  
    workdays = models.ManyToManyField(Workday) 
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='schedules',  
        null=True
    )
    def __str__(self):
        return f"{self.employee.employee_id} - {self.shift.name} - {', '.join([day.day for day in self.workdays.all()])}"

class TemporaryShift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,blank=True,null=True,default=None)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE,blank=True,null=True,default=None)
    date = models.DateField() 
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='temp_shifts',null=True,blank=True,default=None)
    
class WorkHours(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True, blank=True)  
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)  
    date = models.DateField()  
    total_hours = models.DurationField() 
    overtime_hours = models.DurationField(null=True, blank=True)  

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.total_hours}"      


class Holiday(models.Model):
    """
    ছুটির দিনগুলি সংরক্ষণের জন্য Holiday মডেল।
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True,blank=True,default=None) 
    date = models.DateField()  
    reason = models.CharField(max_length=255)  
    def __str__(self):
        return f"{self.reason} - {self.date}"


def get_upload_path(instance, filename):
    # Get the company name from the instance
    if instance.company:
        company_name = instance.company.name
        # Sanitize the company name to avoid invalid characters in the filename
        company_name = company_name.replace(' ', '_')  # Replace spaces with underscores
        company_name = ''.join(c for c in company_name if c.isalnum() or c in ['_', '-'])  # Allow alphanumeric characters, underscores, and hyphens

        # Return the path using the company name
        return os.path.join('uploads', 'notics', company_name, filename)
    
    # Default path if company is not set (e.g., during model creation before save)
    return os.path.join('uploads', 'notics', filename)

class Notice(models.Model):
    TARGET_CHOICES = [
        ('ALL', 'All Departments'),
        ('DEPT', 'Specific Departments'),
        ('USER', 'Specific Users'),
    ]

    title = models.CharField(max_length=255)
    content = RichTextUploadingField()  
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notices')
    department = models.ManyToManyField(Department, blank=True, related_name='notices')
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='user_notices',
        null=True,  
        blank=True
    )
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES, default='ALL')
    file = models.FileField(upload_to=get_upload_path, blank=True, null=True)  
    
    created_at = models.DateTimeField(auto_now_add=True)



