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