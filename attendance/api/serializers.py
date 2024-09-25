from rest_framework import serializers
from ..models import Attendance, AttendanceLog

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, data):
        """
        Validate to ensure the user is active under the company.
        """
        user = data.get('user')
        if not user.is_company_active:
            raise serializers.ValidationError("User is not active under the company.")
        return data

class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = '__all__'

    def validate(self, data):
        """
        Validate to ensure the user is active under the company.
        """
        user = data.get('user')
        if not user.is_company_active:
            raise serializers.ValidationError("User is not active under the company.")
        return data
