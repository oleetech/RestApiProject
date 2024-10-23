# forms.py
from django import forms
from .models import Employee,Department
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'  # Use all fields in the Employee model

    def __init__(self, *args, **kwargs):
        # Extract request object from kwargs
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Filter the user field based on the request user's company or superuser status
        if self.request and self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                # If the user is a superuser, show all users
                self.fields['user'].queryset = get_user_model().objects.all()
            else:
                # Otherwise, filter users by the request user's company
                company = self.request.user.company
                if company:
                    # Show users from the same company
                    self.fields['user'].queryset = get_user_model().objects.filter(company=company)
                else:
                    # If the user doesn't have a company, show an empty queryset
                    self.fields['user'].queryset = get_user_model().objects.none()

        # Optionally hide the company field for non-superusers
        if not self.request.user.is_superuser:
            self.fields.pop('company', None)  # Remove company field for non-superusers
    
from .models import Notice    
from django_ckeditor_5.widgets import CKEditor5Widget  
class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'department', 'user', 'target_type','file']
        widgets = {
            'content': CKEditor5Widget(config_name='default'), 
        }

from .models import LeaveRequest    
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = '__all__'  # LeaveRequest মডেলের সব ফিল্ড ব্যবহার করা হবে

    def __init__(self, *args, **kwargs):
        # Request অবজেক্ট গ্রহণ করা
        self.request = kwargs.pop('request', None)
        # সুপার ক্লাসের __init__ পদ্ধতি কল করা
        super().__init__(*args, **kwargs)

        # প্রমাণীকৃত ব্যবহারকারী কিনা তা যাচাই করা
        if self.request and self.request.user.is_authenticated:
            # চেক করুন ব্যবহারকারী সুপার ইউজার নয় কিনা
            if not self.request.user.is_superuser:
                # Non-superuser এর জন্য company ফিল্ড সরিয়ে ফেলুন
                self.fields.pop('company', None)

            # Superuser হলে, সমস্ত ব্যবহারকারী দেখান
            if self.request.user.is_superuser:
                self.fields['user'].queryset = get_user_model().objects.all()
            else:
                # Non-superuser হলে শুধু একই কোম্পানির ব্যবহারকারী দেখান
                company = self.request.user.company
                if company:
                    # একই কোম্পানির ব্যবহারকারীদের দেখান
                    self.fields['user'].queryset = get_user_model().objects.filter(company=company)
                else:
                    # যদি কোম্পানি না থাকে, তাহলে খালি queryset দেখান
                    self.fields['user'].queryset = get_user_model().objects.none()

            # LeaveType এর queryset নির্ধারণ
            if self.request.user.is_superuser:
                # যদি ব্যবহারকারী সুপারইউজার হয়, তবে সমস্ত LeaveType দেখান
                self.fields['leave_type'].queryset = LeaveType.objects.all()
            else:
                # Non-superuser হলে শুধু একই কোম্পানির LeaveType দেখান
                company = self.request.user.company
                if company:
                    # একই কোম্পানির LeaveType দেখান
                    self.fields['leave_type'].queryset = LeaveType.objects.filter(company=company)
                else:
                    # যদি কোম্পানি না থাকে, তবে খালি queryset দেখান
                    self.fields['leave_type'].queryset = LeaveType.objects.none()

            # Check if the user has permission to approve department leaves
            if not self.request.user.has_perm('attendance.can_approve_department_leave') and not self.request.user.is_superuser:
                # If user does not have permission and is not a superuser, hide the department_approved field
                self.fields.pop('department_approved', None)

            # Check if the user has permission to approve HR leaves
            if not self.request.user.has_perm('attendance.can_approve_hr_leave') and not self.request.user.is_superuser:
                # If user does not have permission and is not a superuser, hide the hr_approved field
                self.fields.pop('hr_approved', None)                

from .models import LeaveType    

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = '__all__'  # LeaveType মডেলের সব ফিল্ড ব্যবহার করা হবে

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Check if the request is authenticated
        if self.request and self.request.user.is_authenticated:
            # Check if the request user is not a superuser
            if not self.request.user.is_superuser:
                # Non-superuser এর জন্য company ফিল্টার করা
                self.fields.pop('company', None)  # Remove company field for non-superusers


                