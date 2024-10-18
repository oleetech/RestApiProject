from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator  
from django.core.exceptions import ValidationError, PermissionDenied  
from .validators import validate_company_name  
from guardian.shortcuts import assign_perm, remove_perm


from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Subscription(models.Model):
    PACKAGE_CHOICES = [
        ('Free', _('Free')),
        ('Standard', _('Standard')),
        ('Premium', _('Premium')),
        ('Enterprise', _('Enterprise')),
    ]

    # Subscription name with choices
    name = models.CharField(
        max_length=50,
        choices=PACKAGE_CHOICES,
        default='Free',
        verbose_name=_('Subscription Plan'),
        help_text=_('Choose the subscription package.')
    )
    
    # Price of the subscription
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Price'),
        help_text=_('Enter the price of the subscription.')
    )
    
    # Maximum number of employees allowed
    max_employees = models.IntegerField(
        default=10,
        verbose_name=_('Maximum Employees'),
        help_text=_('Specify the maximum number of employees allowed for this subscription.')
    )
    
    # Maximum storage capacity (in MB or GB as per your requirement)
    max_storage = models.IntegerField(
        default=10,
        verbose_name=_('Maximum Storage'),
        help_text=_('Specify the maximum storage limit in units (e.g., MB or GB).')
    )
    
    # Boolean field to indicate access to advanced features
    advanced_features = models.BooleanField(
        default=False,
        verbose_name=_('Access to Advanced Features'),
        help_text=_('Indicates whether the subscription includes advanced features.')
    )
    
    # Limits for users and devices
    user_limit = models.PositiveIntegerField(
        default=0,
        verbose_name=_('User Limit'),
        help_text=_('Specify the maximum number of users for this subscription.')
    )
    
    device_limit = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Device Limit'),
        help_text=_('Specify the maximum number of devices that can be connected.')
    )

    # Additional feature limits with various types
    attendance_record_limit = models.BooleanField(
        default=False,
        verbose_name=_('Attendance Record Limit'),
        help_text=_('Indicates if there is a limit on attendance records.')
    )
    
    leave_request_limit = models.BooleanField(
        default=False,
        verbose_name=_('Leave Request Limit'),
        help_text=_('Indicates if there is a limit on leave requests.')
    )
    
    overtime_hours_limit = models.BooleanField(
        default=False,
        verbose_name=_('Overtime Hours Limit'),
        help_text=_('Indicates if there is a limit on overtime hours tracked.')
    )
    
    payroll_cycle_limit = models.BooleanField(
        default=False,
        verbose_name=_('Payroll Cycle Limit'),
        help_text=_('Indicates if there is a limit on payroll cycles per month.')
    )
    
    report_generation_limit = models.BooleanField(
        default=False,
        verbose_name=_('Report Generation Limit'),
        help_text=_('Indicates if there is a limit on the number of reports that can be generated.')
    )

    # Meta class for constraints
    class Meta:
        unique_together = ('name', 'price')  # Unique constraint for name and price
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
    
    def __str__(self):
        return self.name

    def clean(self):
        # Custom validation
        if self.max_employees < 0:
            raise ValidationError(_('Maximum employees cannot be negative.'))
        if self.max_storage < 0:
            raise ValidationError(_('Maximum storage cannot be negative.'))
        if self.price < 0:
            raise ValidationError(_('Price cannot be negative.'))

        # Example of additional custom validation
        if self.user_limit < 0:
            raise ValidationError(_('User limit cannot be negative.'))
        if self.device_limit < 0:
            raise ValidationError(_('Device limit cannot be negative.'))




class Company(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Company Name"),
        help_text=_("Enter the official name of the company (must not contain numbers)."),
        validators=[
            MinLengthValidator(3),
            RegexValidator(regex=r'^[^\d]*$', message=_("Company name must not contain numbers."))
        ]
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Company Address"),
        help_text=_("Enter the full address of the company.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active?"),
        help_text=_("Indicates whether the company is currently active.")
    )
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Subscription Plan"),
        help_text=_("Select the subscription plan for the company.")
    )
    employee_limit = models.IntegerField(
        default=10,
        verbose_name=_("Employee Limit"),
        help_text=_("Maximum number of employees allowed in this company.")
    )
    logo = models.ImageField(
        upload_to='uploads/company_logos/',
        blank=True,
        null=True,
        verbose_name=_("Company Logo"),
        help_text=_("Upload the company's official logo.")
    )

    class Meta:
        # Table name in the database
        db_table = 'company'

        # Singular and plural verbose names
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

        # Default ordering
        ordering = ['-name']  # Descending order by name

        # Custom permissions
        permissions = [
            ('can_view_employee_data', 'Can view employee data'),
            ('can_manage_subscription', 'Can manage company subscription'),
        ]

        # Unique constraint based on name and address
        constraints = [
            models.UniqueConstraint(fields=['name', 'address'], name='unique_company_name_address'),
            models.CheckConstraint(check=models.Q(employee_limit__gt=0), name='check_employee_limit_positive'),
        ]

        # Abstract model inheritance option
        abstract = False

        # Indexing certain fields
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]


    # Model-level validation in the clean method
    def clean(self):
        super().clean()
        if self.address and len(self.address) > 255:
            raise ValidationError(_("Address must not exceed 255 characters."))
        if self.is_active and not self.address:
            raise ValidationError(_("Active companies must have an address."))
            
    # Custom field-level validation for employee_limit
    def clean_employee_limit(self):
        if self.employee_limit <= 0:
            raise ValidationError(_("Employee limit must be a positive number."))
        return self.employee_limit


    def save(self, *args, **kwargs):
        self.clean()  # Call clean method for validation before saving
        super().save(*args, **kwargs)

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

    # Class methods for managing companies
    @classmethod
    def create_company(cls, user, **kwargs):
        company = cls(**kwargs)
        company.full_clean()  # Validate the model
        company.save()        # Save the model instance
        company.assign_permissions(user)  # Assign object-level permissions
        return company

    @classmethod
    def update_company(cls, user, instance, **kwargs):
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.full_clean()  # Ensure all validations are met
        instance.save()        # Save the model instance

    @classmethod
    def delete_company(cls, instance):
        instance.delete()

    @classmethod
    def get_company(cls, user, pk):
        return cls.objects.get(pk=pk)

    @classmethod
    def get_all_companies(cls, user):
        return cls.objects.all()

    def get_subscription_details(self):
        if self.subscription:
            return f"Company is on {self.subscription.name} plan with max employees {self.subscription.max_employees}"
        return "No subscription plan assigned"

    @property
    def is_inactive(self):
        return not self.is_active

    def __str__(self):
        return self.name




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
        return self.username            