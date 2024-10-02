from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from  ..models import Company, CustomUser

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the Company model.
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'is_active']
        
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'mobileNo', 'company', 'password']     
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Validate the password with Django's password validators
        password = validated_data.pop('password')
        validate_password(password)
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)  # Set the hashed password
        user.save()
        return user