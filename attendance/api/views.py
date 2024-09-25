from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Attendance, AttendanceLog
from .serializers import AttendanceSerializer, AttendanceLogSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance using JWT Authentication.
    """
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return attendance data according to the logged-in user's company.
        """
        user = self.request.user
        return Attendance.objects.filter(company=user.company)

    def create(self, request, *args, **kwargs):
        """
        Custom create function for attendance.
        Checks if the user's company and user are active.
        """
        user = request.user
        
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি প্রদান করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        Save the user and their company when creating attendance.
        """
        serializer.save(user=self.request.user, company=self.request.user.company)

    def update(self, request, *args, **kwargs):
        """
        Custom update function for attendance.
        Checks if the user's company and user are active.
        """
        user = request.user
        
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি আপডেট করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        Save updated attendance information.
        """
        serializer.save()

class AttendanceLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attendance logs using JWT Authentication.
    """
    serializer_class = AttendanceLogSerializer
    queryset = AttendanceLog.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return attendance log data according to the logged-in user's company.
        """
        user = self.request.user
        return AttendanceLog.objects.filter(company=user.company)

    def create(self, request, *args, **kwargs):
        """
        Custom create function for attendance log.
        Checks if the user's company and user are active.
        """
        user = request.user
        
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি লগ প্রদান করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        Save the user and their company when creating attendance log.
        """
        serializer.save(user=self.request.user, company=self.request.user.company)
