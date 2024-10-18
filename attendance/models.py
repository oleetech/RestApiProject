from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company 
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat

class Employee(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

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

    RELIGION_CHOICES = [
        ('Christianity', 'Christianity'),
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Buddhism', 'Buddhism'),
        ('Sikhism', 'Sikhism'),
        ('Judaism', 'Judaism'),
        ('Other', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_employees',
        verbose_name=_("Company"),
        null=True, blank=True,
    )
    employee_id = models.CharField(
        max_length=20,
        verbose_name=_("Employee ID"),
    )
    first_name = models.CharField(max_length=50, null=True, blank=True,  verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50,null=True, blank=True,  verbose_name=_("Last Name"))
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Full Name"), editable=False)


    department = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Department name"))  
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Position title"))  
    contact_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("Contact number"))  

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default="M")
    bloodGroup = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES,blank=True, null=True)
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES,blank=True, null=True)
    maritalStatus = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES,blank=True, null=True)    
    date_of_joining = models.DateField(null=True, blank=True, verbose_name=_("Date of joining"))  
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_("Email Address"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
 
    class Meta:
        verbose_name = _("Employee")  
        verbose_name_plural = _("Employees")  
        ordering = ['date_of_joining']  
        constraints = [
            # Unique constraint per company for employee ID
            models.UniqueConstraint(fields=['company', 'employee_id'], name='unique_employee_per_company'),
            # Ensure unique contact number
            models.UniqueConstraint(fields=['contact_number'], name='unique_contact_number'),
            # Ensure unique email
            models.UniqueConstraint(fields=['email'], name='unique_email'),
            # Ensure date of birth is before the date of joining
            models.CheckConstraint(check=models.Q(date_of_birth__lt=models.F('date_of_joining')), name='check_birth_before_joining'),
            # Ensure employee ID is alphanumeric
            models.CheckConstraint(check=models.Q(employee_id__regex=r'^[a-zA-Z0-9]+$'), name='check_employee_id_alphanumeric'),
            # Ensure contact number is numeric
            models.CheckConstraint(check=models.Q(contact_number__regex=r'^[0-9]+$'), name='check_contact_number_numeric'),
            # Ensure email contains "@" symbol
            models.CheckConstraint(check=models.Q(email__contains='@'), name='check_valid_email'),
            # Ensure date of birth is after a reasonable minimum date (e.g., 1900-01-01)
            models.CheckConstraint(check=models.Q(date_of_birth__gt='1900-01-01'), name='check_valid_birth_date'),
            # Ensure the date of joining is not in the future
            models.CheckConstraint(check=models.Q(date_of_joining__lte=models.functions.Now()), name='check_valid_joining_date'),
        ]
    def save(self, *args, **kwargs):
        """
        Save method that checks the company's employee limit before adding a new employee.
        """
        if self.company:  # Check if the employee has a company assigned
            # Count the current number of employees in the company
            current_employee_count = self.company.company_employees.count()
            max_employees_allowed = self.company.subscription.max_employees

            # Check if the current number of employees exceeds the allowed limit
            if current_employee_count >= max_employees_allowed:
                raise ValidationError(
                    f"Cannot add more employees. The maximum limit of {max_employees_allowed} employees for this company's subscription has been reached."
                )
        
        # Call the original save method
        super().save(*args, **kwargs)

        
    def __str__(self):
        return f"({self.employee_id} {self.first_name})"  

    def clean(self):
        super().clean()

        # Ensure either first or last name is provided
        if not self.first_name and not self.last_name:
            raise ValidationError(_("At least one of First Name or Last Name must be provided."))
        # Validate email format (simple regex)
        if self.email and '@' not in self.email:
            raise ValidationError(_("Email address must contain a valid '@' symbol."))


        if self.contact_number and not self.contact_number.isdigit():
            raise ValidationError(_("Contact number must be numeric."))  
        if len(self.contact_number) < 10 or len(self.contact_number) > 15:
            raise ValidationError(_("Contact number must be between 10 and 15 digits."))  
    @property
    def full_name(self):
        """Return the full name of the employee if user has first and last name."""
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def get_department_and_position(self):
        """Return a string representation of department and position."""
        return f"{self.position} in {self.department}" if self.department and self.position else _("No specific department or position assigned.") 


class EmployeeDocument(models.Model):
    EMPLOYEE_DOCUMENT_TYPES = (
        ('Resume', 'Resume'),
        ('Contract', 'Contract'),
        ('ID Card', 'ID Card'),
        ('Other', 'Other'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Associate the document with an employee (User model in this case)
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
        if len(self.serial_number) < 10:
            raise ValidationError("Serial number must be at least 10 characters long.")
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
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_logs',
        verbose_name=_("Employee")
    )
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
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Employee linked to the schedule
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)  # The shift they are assigned to
    workdays = models.ManyToManyField(Workday)  # Allow multiple workdays
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='schedules',  # Changed related_name to 'schedules'
        null=True
    )
    def __str__(self):
        # Using employee_id and position from Employee model
        return f"{self.employee.employee_id} - {self.shift.name} - {', '.join([day.day for day in self.workdays.all()])}"

class TemporaryShift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()  # অস্থায়ী শিফটের নির্দিষ্ট তারিখ
    company = models.ForeignKey(Company, on_delete=models.CASCADE,related_name='temp_shifts')
    
class WorkHours(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Employee linked to the work hours
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)  # Linking work hours with company
    date = models.DateField()  # Date for which hours are calculated
    total_hours = models.DurationField()  # Total worked hours
    overtime_hours = models.DurationField(null=True, blank=True)  # Optional overtime hours

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.total_hours}"      


class Holiday(models.Model):
    """
    ছুটির দিনগুলি সংরক্ষণের জন্য Holiday মডেল।
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # কোম্পানিভিত্তিক ছুটি
    date = models.DateField()  # ছুটির তারিখ
    reason = models.CharField(max_length=255)  # ছুটির কারণ যেমন ঈদ, পুজা ইত্যাদি

    def __str__(self):
        return f"{self.reason} - {self.date}"
