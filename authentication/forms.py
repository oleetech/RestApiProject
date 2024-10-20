# forms.py
from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'mobileNo', 'company']  # Include fields to update
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobileNo': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')  # Get the user instance passed in the form
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if user and user.company:  # If company is already set, disable the company field
            self.fields['company'].disabled = True
