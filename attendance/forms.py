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