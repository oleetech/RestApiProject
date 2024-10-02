from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company  # Correctly import the Company model
from datetime import timedelta
from django.utils import timezone

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employees')  # Link to Django's User model
    employee_id = models.CharField(max_length=20, unique=True)   # Unique Employee ID
    department = models.CharField(max_length=50, null=True, blank=True)  # Department name
    position = models.CharField(max_length=50, null=True, blank=True)  # Position title
    contact_number = models.CharField(max_length=15, null=True, blank=True)  # Contact Number
    date_of_joining = models.DateField(null=True, blank=True)  # Date of joining

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['date_of_joining']  # Order employees by date of joining

    def __str__(self):
        return f"{self.user.username} ({self.employee_id})"  # More informative string representation

    def clean(self):
        """
        Custom validation logic can be implemented here.
        """
        if self.contact_number and not self.contact_number.isdigit():
            raise ValidationError("Contact number must be numeric.")
        if len(self.contact_number) < 10 or len(self.contact_number) > 15:
            raise ValidationError("Contact number must be between 10 and 15 digits.")

    @property
    def full_name(self):
        """
        Return the full name of the employee if user has first and last name.
        """
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def get_department_and_position(self):
        """
        Return a string representation of department and position.
        """
        return f"{self.position} in {self.department}" if self.department and self.position else "No specific department or position assigned."

class Device(models.Model):
    device_id = models.CharField(max_length=50, unique=True)  # Device ID assigned by the system
    location = models.CharField(max_length=100)  # Physical location of the device
    description = models.TextField(null=True, blank=True)  # Device description
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Device IP Address
    last_sync_time = models.DateTimeField(null=True, blank=True)  # Last time the device was synced
    serial_number = models.CharField(max_length=255, unique=True,null=True)  # Unique serial number of the device
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)  # Link to the company

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"
        ordering = ['-last_sync_time']  # Order devices by last sync time (latest first)

    def __str__(self):
        """
        Return a string representation of the device showing its ID and location.
        """
        return f"{self.device_id} - {self.location}"

    def clean(self):
        """
        Custom validation logic to ensure the device has a valid serial number format.
        """
        if len(self.serial_number) < 10:
            raise ValidationError("Serial number must be at least 10 characters long.")
        if not self.ip_address:
            raise ValidationError("Device must have a valid IP address.")

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
    
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_logs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_logs',null=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
   
    STATUS_CHOICES = [
        ('IN', 'Check-In'),
        ('OUT', 'Check-Out'),
        ('BREAK_IN', 'Break-In'),
        ('BREAK_OUT', 'Break-Out'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    mode = models.CharField(max_length=10, choices=[('FP', 'Fingerprint'), ('CARD', 'Card'), ('PWD', 'Password'), ('GPS', 'GPS-based')],default='FP')

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
        ordering = ['-timestamp']  # Order by latest timestamp first
        constraints = [
            models.UniqueConstraint(fields=['employee', 'timestamp'], name='unique_attendance_log_per_user_per_day_per_checkin')
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


class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Employee linked to the schedule
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)  # The shift they are assigned to
    workday = models.CharField(max_length=10, choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')])  # Workday

    def __str__(self):
        return f"{self.employee.user.username} - {self.shift.name} - {self.workday}"


class WorkHours(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Employee linked to the work hours
    date = models.DateField()  # Date for which hours are calculated
    total_hours = models.DurationField()  # Total worked hours
    overtime_hours = models.DurationField(null=True, blank=True)  # Optional overtime hours

    def __str__(self):
        return f"{self.employee.user.username} - {self.date} - {self.total_hours}"           