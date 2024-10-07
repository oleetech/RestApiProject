# validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_company_name(value):
    if len(value) < 3:
        raise ValidationError(_("Company name must be at least 3 characters long."))
    if any(char.isdigit() for char in value):
        raise ValidationError(_("Company name must not contain numbers."))
