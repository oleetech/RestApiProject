from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator  
from django.core.exceptions import ValidationError, PermissionDenied  
from .validators import validate_company_name  
from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import UserObjectPermission



class Company(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(regex=r'^[^\d]*$', message=_("Company name must not contain numbers."))
        ]
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ("authentication.change_company", _("Can change company")),
            ("authentication.delete_company", _("Can delete company")),
            ("authentication.view_company", _("Can view company")),
            ("authentication.add_company", _("Can add company")),
            ("authentication.activate_company", _("Can activate company")),
            ("authentication.deactivate_company", _("Can deactivate company")),

        ]

    def __str__(self):
        return self.name

    @property
    def is_inactive(self):
        return not self.is_active

    def clean(self):
        super().clean()
        if self.address and len(self.address) > 255:
            raise ValidationError(_("Address must not exceed 255 characters."))
        if self.is_active and not self.address:
            raise ValidationError(_("Active companies must have an address."))

    def save(self, *args, **kwargs):
        self.clean()  # Call clean method for validation before saving
        super().save(*args, **kwargs)

    # Permissions using django-guardian
    def assign_permissions(self, user):
        """Assign permissions to a user for this company."""
        assign_perm('view_company', user, self)
        assign_perm('change_company', user, self)
        assign_perm('delete_company', user, self)

    def remove_permissions(self, user):
        """Remove permissions from a user for this company."""
        remove_perm('view_company', user, self)
        remove_perm('change_company', user, self)
        remove_perm('delete_company', user, self)

    @classmethod
    def create_company(cls, user, **kwargs):
        if not user.has_perm('authentication.add_company'):
            raise PermissionDenied("You do not have permission to add a company.")

        company = cls(**kwargs)
        company.full_clean()  # Validate the model
        company.save()        # Save the model instance
        company.assign_permissions(user)  # Assign object-level permissions
        return company

    @classmethod
    def update_company(cls, user, instance, **kwargs):
        if not user.has_perm('change_company', instance):
            raise PermissionDenied("You do not have permission to change this company.")

        for field, value in kwargs.items():
            if field == 'name':
                instance.name = value
            elif field == 'address':
                instance.address = value
            elif field == 'is_active':
                instance.is_active = value

        instance.full_clean()  # Ensure all validations are met
        instance.save()        # Save the model instance

    @classmethod
    def delete_company(cls, user, instance):
        if not user.has_perm('delete_company', instance):
            raise PermissionDenied("You do not have permission to delete this company.")
        instance.delete()

    @classmethod
    def get_company(cls, user, pk):
        company = cls.objects.get(pk=pk)
        if not user.has_perm('view_company', company):
            raise PermissionDenied("You do not have permission to view this company.")
        return company

    @classmethod
    def get_all_companies(cls, user):
        if not user.has_perm('view_company'):
            raise PermissionDenied("You do not have permission to view companies.")
        return cls.objects.all()



# CustomUserManager creates a custom user.
class CustomUserManager(BaseUserManager):
    """
    CustomUserManager inherits from Django's BaseUserManager.
    We create custom methods for user and superuser creation.
    """

    # Method for creating a standard user
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Method for creating a standard user.
        """
        if not email:  # Raise an error if email is not provided
            raise ValueError('The Email field must be set')

        # Normalizing email
        email = self.normalize_email(email)

        # Create user object with email, username, and extra fields
        user = self.model(email=email, username=username, **extra_fields)

        # Set the user's password
        user.set_password(password)

        # Save the user object to the database
        user.save(using=self._db)
        return user

    # Method for creating a superuser
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Method for creating a superuser.
        """

        # Set default fields for superuser
        extra_fields.setdefault('is_staff', True)  # Superuser must be staff
        extra_fields.setdefault('is_superuser', True)  # Superuser must be a superuser

        # Raise error if is_staff is False
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        # Raise error if is_superuser is False
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Create superuser using create_user method
        return self.create_user(email, username, password, **extra_fields)


# CustomUser model definition
class CustomUser(AbstractUser):
    """
    Custom user model that inherits from Django's AbstractUser.
    We can add custom fields and methods as required.
    """

    # Custom fields
    email = models.EmailField(unique=True, validators=[EmailValidator()])  # Email must be unique and validated
    mobileNo = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Mobile number must be in the format: '+999999999'. Up to 15 digits allowed.")
        ]
    )  # Mobile number with regex validation
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, related_name='employees', null=True, blank=True)  # Company can be null
    is_company_active = models.BooleanField(default=True)  # Indicates if the associated company is active

    # Adding a custom manager
    objects = CustomUserManager()  # Using the CustomUserManager for user creation

    # Setting email as username field
    USERNAME_FIELD = 'email'  # Use email for login
    REQUIRED_FIELDS = ['username']  # Username is required alongside email



    @property
    def full_name(self):
  
        return f"{self.first_name} {self.last_name}".strip()  # Full name combining first and last names

    def is_active_company(self):

        return self.company.is_active if self.company else False  # Check if the company is active

    def clean(self):

        super().clean()  # Call the parent class's clean method

        # Custom validation: Check if the mobile number is provided and if the company is active
        if self.mobileNo and not self.is_company_active:
            raise ValidationError("Cannot assign a mobile number if the associated company is inactive.")

    def __str__(self):
        """
        Return the user's email as a string.
        """
        return self.email            