from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company  # Correctly import the Company model
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

    def __str__(self):
        return f"{self.device_id} - {self.location}"




        
class AttendanceLog(models.Model):
    """
    ব্যবহারকারীর চেক ইন এবং চেক আউট তথ্য সংরক্ষণ করার জন্য উপস্থিতি লগ মডেল।
    """
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_logs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_logs')
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
        constraints = [
            models.UniqueConstraint(fields=['employee', 'timestamp'], name='unique_attendance_log_per_user_per_day_per_checkin')
        ]


class Shift(models.Model):
    name = models.CharField(max_length=50)  # Name of the shift
    start_time = models.TimeField()  # Shift start time
    end_time = models.TimeField()  # Shift end time
    break_duration = models.DurationField(null=True, blank=True)  # Optional break duration

    def __str__(self):
        return self.name


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