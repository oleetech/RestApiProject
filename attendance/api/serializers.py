from rest_framework import serializers
from ..models import  Employee, Device, AttendanceLog, Shift, Schedule, WorkHours
from datetime import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import ipaddress
# Serializer for Employee model
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'user', 'employee_id', 'department', 'position', 'contact_number', 'date_of_joining']

    # Custom validation for employee ID
    def validate_employee_id(self, value):
        """
        Ensure employee ID is unique and meets specific format requirements.
        """
        if not value.isalnum():
            raise serializers.ValidationError(_("Employee ID must be alphanumeric."))  # Translatable error
        return value

    # Custom validation for contact number
    def validate_contact_number(self, value):
        """
        Validate that contact number has 10-15 digits.
        """
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError(_("Contact number must be between 10 and 15 digits."))  # Translatable error
        if not value.isdigit():
            raise serializers.ValidationError(_("Contact number must be numeric."))  # Translatable error
        return value

    # Cross-field validation (e.g., department and position should be provided together)
    def validate(self, data):
        if data.get('department') and not data.get('position'):
            raise serializers.ValidationError(_("Position must be provided if department is specified."))  # Translatable error
        return data


# Serializer for Device model
class DeviceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)  # Add company name in response

    class Meta:
        model = Device
        fields = ['id', 'device_id', 'location', 'description', 'ip_address', 'last_sync_time', 'serial_number', 'company', 'company_name']  # Added 'company', 'company_name' and 'serial_number'

    def validate_device_id(self, value):
        """
        Ensure the device ID is unique and follows certain rules.
        """
        if Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("A device with this ID already exists.")
        return value

    def validate_ip_address(self, value):
        """
        Ensure valid IP address format and that it falls within a specific IP range if required.
        """
        try:
            ip = ipaddress.ip_address(value)
            # Example: Restrict to private IP ranges only (for internal devices)
            if not ip.is_private:
                raise serializers.ValidationError("IP address must be within a private range (e.g., 192.168.x.x).")
        except ValueError:
            raise serializers.ValidationError("Invalid IP address format.")
        return value

    def validate_serial_number(self, value):
        """
        Ensure the serial number is unique.
        """
        if Device.objects.filter(serial_number=value).exists():
            raise serializers.ValidationError("A device with this serial number already exists.")
        return value

    def validate(self, data):
        """
        Custom validation for various fields.
        - Ensure last sync time is not in the future.
        """
        # if data.get('last_sync_time') and data['last_sync_time'] > datetime.now():
        #     raise serializers.ValidationError("Last sync time cannot be in the future.")

        # Additional validations (if required)
        # Example: Ensure the device location is not left empty
        if 'location' in data and not data['location'].strip():
            raise serializers.ValidationError("Device location cannot be empty.")

        return data

    def create(self, validated_data):
        """
        Customize device creation logic if needed.
        """
        # You can modify the data before saving, e.g., auto-assign company based on user session
        # Example: If you want to assign a default company:
        if 'company' not in validated_data:
            validated_data['company'] = self.context['request'].user.company

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Customize device update logic if needed.
        """
        # Add any specific update logic here if needed.
        return super().update(instance, validated_data)


class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = [
            'id', 'employee', 'company', 'device', 'timestamp', 
            'status', 'mode', 'locationName', 'latitude', 'longitude'
        ]

    def validate(self, data):
        """
        Validate the employee's active status in the company and ensure that the timestamp is valid.
        """
        employee = data.get('employee')

        # Ensure the employee is active under the company
        if not employee.is_active or not employee.company == data.get('company'):
            raise serializers.ValidationError("Employee is not active or does not belong to the specified company.")

        # Use timezone.now() to get the current time in a timezone-aware manner
        current_time = timezone.now()

        # Ensure the timestamp is not in the future
        if data['timestamp'] > current_time:
            raise serializers.ValidationError("Timestamp cannot be set in the future.")

        return data

    def validate_status(self, value):
        """
        Ensure that the attendance status is valid.
        """
        valid_statuses = ['IN', 'OUT', 'BREAK_IN', 'BREAK_OUT']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid attendance status. Must be one of {valid_statuses}.")
        return value

# Serializer for Shift model
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id', 'name', 'start_time', 'end_time', 'break_duration', 'company', 'status']  # Added necessary fields

    # Custom validation for the company field
    def validate_company(self, value):
        """
        Ensure the company is active.
        """
        if value and not value.is_active:
            raise serializers.ValidationError("The company must be active.")
        return value

    # Custom validation for start and end time
    def validate(self, data):
        """
        Ensure start time is before end time.
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        return data

    # Custom validation for break duration
    def validate_break_duration(self, value):
        """
        Ensure break duration is not negative.
        """
        if value and value.total_seconds() < 0:
            raise serializers.ValidationError("Break duration cannot be negative.")
        return value
# Serializer for Schedule model
class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'employee', 'shift', 'workday']

    def validate_workday(self, value):
        """
        Ensure valid workday.
        """
        valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        if value not in valid_days:
            raise serializers.ValidationError("Invalid workday.")
        return value


# Serializer for WorkHours model
class WorkHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkHours
        fields = ['id', 'employee', 'date', 'total_hours', 'overtime_hours']

    def validate(self, data):
        """
        Validate that total hours and overtime hours are positive.
        """
        if data['total_hours'].total_seconds() <= 0:
            raise serializers.ValidationError("Total hours worked must be positive.")
        
        if data.get('overtime_hours') and data['overtime_hours'].total_seconds() < 0:
            raise serializers.ValidationError("Overtime hours cannot be negative.")
        
        return data
