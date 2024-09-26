from rest_framework import serializers
from ..models import  Employee, Device, AttendanceLog, Shift, Schedule, WorkHours
from datetime import datetime

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
            raise serializers.ValidationError("Employee ID must be alphanumeric.")
        return value

    # Custom validation for contact number
    def validate_contact_number(self, value):
        """
        Validate that contact number has 10-15 digits.
        """
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Contact number must be between 10 and 15 digits.")
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must be numeric.")
        return value

    # Cross-field validation (e.g., department and position should be provided together)
    def validate(self, data):
        if data.get('department') and not data.get('position'):
            raise serializers.ValidationError("Position must be provided if department is specified.")
        return data


# Serializer for Device model
class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'device_id', 'location', 'description', 'ip_address', 'last_sync_time']

    def validate_ip_address(self, value):
        """
        Ensure valid IP address format.
        """
        # You can add further custom validation if needed for specific IP ranges.
        return value

    def validate(self, data):
        """
        Validate last sync time should not be in the future.
        """
        if data.get('last_sync_time') and data['last_sync_time'] > datetime.now():
            raise serializers.ValidationError("Last sync time cannot be in the future.")
        return data


# Serializer for AttendanceLog model
class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['id', 'employee', 'company', 'device', 'timestamp', 'status', 'mode', 'locationName', 'latitude', 'longitude']

    def validate(self, data):
        """
        Validate to ensure the user is active under the company and timestamp is valid.
        """
        user = data.get('employee').user  # Assuming employee is linked to user
        if not user.is_company_active:
            raise serializers.ValidationError("User is not active under the company.")

        if data['timestamp'] > datetime.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        
        return data

    def validate_status(self, value):
        """
        Ensure valid status for attendance log.
        """
        if value not in ['IN', 'OUT', 'BREAK_IN', 'BREAK_OUT']:
            raise serializers.ValidationError("Invalid attendance status.")
        return value


# Serializer for Shift model
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id', 'name', 'start_time', 'end_time', 'break_duration']

    def validate(self, data):
        """
        Validate that end time is after start time.
        """
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data


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
