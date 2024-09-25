from django.db import models
from django.conf import settings
from authentication.models import CustomUser, Company  # Correctly import the Company model

from django.db import models
from django.conf import settings
from authentication.models import Company  # Assuming Company model is already defined

class Attendance(models.Model):
    """
    উপস্থিতি মডেল, যা সাধারণ উপস্থিতি ডাটাবেস টেবিলের সাথে মেলে।
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    # ব্যবহারকারী এবং কোম্পানির ForeignKey
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendances')

    # উপস্থিতির তারিখ এবং সময়
    date = models.DateField(null=False)  # তারিখ
    checkInTime = models.TimeField(null=False)  # চেক ইন সময়
    checkOutTime = models.TimeField(null=True, blank=True)  # চেক আউট সময় (nullable)

    # চেক ইন লোকেশন তথ্য
    checkInLocationName = models.CharField(max_length=255, null=True, blank=True)  # চেক ইন লোকেশনের নাম
    checkInLatitude = models.FloatField(null=True, blank=True)  # চেক ইন লোকেশনের অক্ষাংশ
    checkInLongitude = models.FloatField(null=True, blank=True)  # চেক ইন লোকেশনের দ্রাঘিমাংশ

    # চেক আউট লোকেশন তথ্য
    checkOutLocationName = models.CharField(max_length=255, null=True, blank=True)  # চেক আউট লোকেশনের নাম
    checkOutLatitude = models.FloatField(null=True, blank=True)  # চেক আউট লোকেশনের অক্ষাংশ
    checkOutLongitude = models.FloatField(null=True, blank=True)  # চেক আউট লোকেশনের দ্রাঘিমাংশ

    # উপস্থিতির অবস্থা
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')  # উপস্থিতি অবস্থা

    # রেকর্ড তৈরি এবং আপডেটের সময়
    createdAt = models.DateTimeField(auto_now_add=True)  # রেকর্ড তৈরি হওয়ার সময়
    updatedAt = models.DateTimeField(auto_now=True)  # রেকর্ড আপডেট হওয়ার সময়

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_attendance_per_user_per_day')
        ]

        
class AttendanceLog(models.Model):
    """
    ব্যবহারকারীর চেক ইন এবং চেক আউট তথ্য সংরক্ষণ করার জন্য উপস্থিতি লগ মডেল।
    """
    # ব্যবহারকারী এবং কোম্পানির ForeignKey
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_logs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_logs')

    # উপস্থিতির তারিখ এবং সময়
    date = models.DateField(null=False)  # তারিখ
    checkInTime = models.TimeField(null=False)  # চেক ইন সময়
    checkOutTime = models.TimeField(null=True, blank=True)  # চেক আউট সময় (nullable)

    # চেক ইন লোকেশন তথ্য
    checkInLocationName = models.CharField(max_length=255, null=True, blank=True)  # চেক ইন লোকেশনের নাম
    checkInLatitude = models.FloatField(null=True, blank=True)  # চেক ইন লোকেশনের অক্ষাংশ
    checkInLongitude = models.FloatField(null=True, blank=True)  # চেক ইন লোকেশনের দ্রাঘিমাংশ

    # চেক আউট লোকেশন তথ্য
    checkOutLocationName = models.CharField(max_length=255, null=True, blank=True)  # চেক আউট লোকেশনের নাম
    checkOutLatitude = models.FloatField(null=True, blank=True)  # চেক আউট লোকেশনের অক্ষাংশ
    checkOutLongitude = models.FloatField(null=True, blank=True)  # চেক আউট লোকেশনের দ্রাঘিমাংশ

    # উপস্থিতির অবস্থা
    status = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ], default='present')  # উপস্থিতি অবস্থা

    # রেকর্ড তৈরি এবং আপডেটের সময়
    createdAt = models.DateTimeField(auto_now_add=True)  # রেকর্ড তৈরি হওয়ার সময়
    updatedAt = models.DateTimeField(auto_now=True)  # রেকর্ড আপডেট হওয়ার সময়

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.checkInTime} - {self.checkOutTime}"

    class Meta:
        # ব্যবহারকারী এবং তারিখ এবং চেক ইন সময় অনুযায়ী ইউনিক constraint
        constraints = [
            models.UniqueConstraint(fields=['user', 'date', 'checkInTime'], name='unique_attendance_log_per_user_per_day_per_checkin')
        ]