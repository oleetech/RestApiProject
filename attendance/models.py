from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company  # Correctly import the Company model

class Attendance(models.Model):
    """
    উপস্থিতি মডেল যেখানে প্রথম চেক ইন এবং শেষ চেক আউট সেভ হবে।
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    # ব্যবহারকারী এবং কোম্পানি
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendances')

    # উপস্থিতির তারিখ
    date = models.DateField(auto_now_add=True)  # তারিখ

    # প্রথম চেক ইন এবং শেষ চেক আউট
    first_check_in_time = models.TimeField(null=False)  # প্রথম চেক ইন সময়
    last_check_out_time = models.TimeField(null=True, blank=True)  # শেষ চেক আউট সময়

    # উপস্থিতির অবস্থা
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    # রেকর্ড তৈরি এবং আপডেটের সময়
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # প্রথম চেক ইন এবং শেষ চেক আউটের লোকেশন
    first_check_in_location_name = models.CharField(max_length=255, null=True, blank=True)
    first_check_in_latitude = models.FloatField(null=True, blank=True)
    first_check_in_longitude = models.FloatField(null=True, blank=True)
    last_check_out_location_name = models.CharField(max_length=255, null=True, blank=True)
    last_check_out_latitude = models.FloatField(null=True, blank=True)
    last_check_out_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_attendance_per_user_per_day')
        ]
        
class AttendanceLog(models.Model):
    """
    চেক ইন এবং চেক আউটের লগ রাখার জন্য মডেল।
    """
    # ব্যবহারকারী এবং উপস্থিতি
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_logs')
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='logs')

    # লগ ইনপুট সময় (চেক ইন বা চেক আউট)
    log_time = models.TimeField()  # ইন বা আউটের সময় লগ হবে
    log_type = models.CharField(max_length=10, choices=[('in', 'Check In'), ('out', 'Check Out')])  # ইন বা আউট

    # লোকেশন তথ্য
    location_name = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.attendance.date} - {self.log_type} - {self.log_time}"
        