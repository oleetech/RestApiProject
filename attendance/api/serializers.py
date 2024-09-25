from rest_framework import serializers
from  ..models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, data):
        """
        Validate করতে হবে ইউজার কোম্পানির অধীনে অ্যাক্টিভ কিনা।
        """
        user = data.get('user')
        if not user.is_company_active:
            raise serializers.ValidationError("User is not active under the company.")
        return data