from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Company(models.Model):
    """
    Model representing a company.
    """
    name = models.CharField(max_length=255, unique=True)  # Unique name for the company
    address = models.CharField(max_length=255, blank=True, null=True)  # Address of the company
    is_active = models.BooleanField(default=True)  # Indicates whether the company is active

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
    This model inherits from `AbstractUser`, allowing us to add custom fields as needed.
    """

    # Additional custom fields
    email = models.EmailField(unique=True)  # Email is defined as unique
    mobileNo = models.CharField(max_length=15, blank=True, null=True)  # Adding mobile number
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='employees', null=True, blank=True) 
    # If a company is deleted, the user will still exist, but company will be set to null.
    is_company_active = models.BooleanField(default=True)
    # Adding custom manager
    objects = CustomUserManager()

    # Setting email as username field
    USERNAME_FIELD = 'email'  # Use email for login
    REQUIRED_FIELDS = ['username']  # Username field is required alongside email

    def __str__(self):
        """
        Return the user's email as a string.
        """
        return self.email
