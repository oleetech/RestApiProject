# forms.py
from django import forms
from .models import Employee
from django.utils.translation import gettext_lazy as _

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ('company',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Get request from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Ensure either first or last name is provided
        if not self.cleaned_data.get('first_name') and not self.cleaned_data.get('last_name'):
            self.add_error(None, _("At least one of First Name or Last Name must be provided."))

        # Validate email format (simple regex)
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            self.add_error('email', _("Email address must contain a valid '@' symbol."))

        # Validate contact number
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number:
            if not contact_number.isdigit():
                self.add_error('contact_number', _("Contact number must be numeric."))
            if len(contact_number) < 10 or len(contact_number) > 15:
                self.add_error('contact_number', _("Contact number must be between 10 and 15 digits."))

        # Check if the user has an associated company
        if self.request and self.request.user.is_authenticated:
            if not self.request.user.company:
                self.add_error('company', _("Company must be set for the user."))
            else:
                # If company exists, you can set it if needed
                self.cleaned_data['company'] = self.request.user.company  

        return self.cleaned_data  # Return cleaned data
    
    
from .models import Notice

# forms.py
from django import forms
from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'notice_type', 'department']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Retrieve the user passed in the admin
        super(NoticeForm, self).__init__(*args, **kwargs)

        # Check user permissions and adjust fields accordingly
        if self.user:
            # Check if the user has permission to add or change global notices
            if not (self.user.has_perm('attendance.add_global_notice') or self.user.has_perm('attendance.change_global_notice')):
                # Add a CSS class to hide the notice_type field
                self.fields['notice_type'].widget.attrs.update({'class': 'hidden'})

                # Automatically set the department to the user's department
                # if hasattr(self.user, 'employee') and self.user.employee.department:
                #     self.fields['department'].initial = self.user.employee.department
                #     # Add a CSS class to hide the department field
                #     self.fields['department'].widget.attrs.update({'class': 'hidden'})

            else:
                # If the user has global notice permissions, keep the notice_type field visible
                # and filter departments based on the user's company
                if hasattr(self.user, 'company'):
                    self.fields['department'].queryset = self.user.company.departments.all()
                else:
                    self.fields['department'].queryset = self.fields['department'].queryset.none()  # No options if no company is set