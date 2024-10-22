# forms.py
from django import forms
from .models import Employee,Department
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ('company',)

    def __init__(self, *args, **kwargs):
        # Extract request object from kwargs
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Filter the user field based on the request user's company
        if self.request and self.request.user.is_authenticated:
            company = self.request.user.company
            if company:
                # Filter users by company if the request user has a company
                self.fields['user'].queryset = get_user_model().objects.filter(company=company)
            else:
                # If the user doesn't have a company, show an empty queryset
                self.fields['user'].queryset = get_user_model().objects.none()
    
from .models import Notice    
from ckeditor.widgets import CKEditorWidget
class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'department', 'user', 'target_type']
        widgets = {
            'content': CKEditorWidget(),  # Use CKEditor 5 for content field
        }