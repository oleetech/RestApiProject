from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .utils import success_response, error_response, validation_error_response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Employee, Device, AttendanceLog, Shift, Schedule, WorkHours
from .serializers import (
    EmployeeSerializer, 
    DeviceSerializer, 
    AttendanceLogSerializer, 
    ShiftSerializer, 
    ScheduleSerializer, 
    WorkHoursSerializer
)

from .permission import AttendanceHasDynamicModelPermission

# ViewSet for Employee
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     if self.request.method in ['GET']:
    #         # No authentication needed for GET requests
    #         permission_classes = [AllowAny]
    #         self.authentication_classes = []  # Remove JWT authentication for GET requests
    #     else:
    #         # Authentication required for other requests
    #         permission_classes = [IsAuthenticated, AttendanceHasDynamicModelPermission]
    #         self.authentication_classes = [JWTAuthentication]  # JWT required for other methods

    #     return [permission() for permission in permission_classes]
    @swagger_auto_schema(
        operation_summary="List Employees",
        operation_description="Retrieve a list of employees belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="A list of employees",
                schema=EmployeeSerializer(many=True)
            ),
            403: openapi.Response(
                description="Permission denied"
            )
        },
        tags=["Employees"]
    )
    def list(self, request, *args, **kwargs):
        """Return an array of employee objects belonging to the request user's company."""
        try:
            # Filter the queryset to get only employees of the user's company
            queryset = self.get_queryset().filter(user__company=request.user.company)

            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return success_response("Employee list retrieved successfully.", serializer.data)
            else:
                return success_response("No employees found.", [])
        except DatabaseError as e:
            return error_response("Database error occurred.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Retrieve Employee",
        operation_description="Retrieve details of a single employee belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="Employee details retrieved successfully",
                schema=EmployeeSerializer()
            ),
            404: openapi.Response(description="Employee not found"),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Employees"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Return a single employee object belonging to the request user's company."""
        try:
            # Get the employee instance
            instance = self.get_object()

            # Check if the employee's company matches the user's company
            if instance.user.company.id != request.user.company.id:
                return error_response("You do not have permission to access this employee.", 
                                    error_type="PermissionDenied", 
                                    status_code=status.HTTP_403_FORBIDDEN)

            # If the employee is in the same company, serialize the data
            serializer = self.get_serializer(instance)
            return success_response(f"Employee {instance.employee_id} details retrieved.", serializer.data)

        except NotFound:
            return error_response("Employee not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Database error occurred.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Create Employee",
        operation_description="Create a new employee and return the created object.",
        request_body=EmployeeSerializer,
        responses={
            201: openapi.Response(
                description="Employee created successfully",
                schema=EmployeeSerializer()
            ),
            400: openapi.Response(description="Validation error")
        },
        tags=["Employees"]
    ) 
    def create(self, request, *args, **kwargs):
        """Create a new employee and return the created object."""
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                return success_response("Employee created successfully.", serializer.data, status_code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return validation_error_response(e.detail)
        except DatabaseError as e:
            return error_response("Server error while creating employee.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Update Employee",
        operation_description="Update an existing employee's details. This is a full update (PUT).",
        request_body=EmployeeSerializer,
        responses={
            200: openapi.Response(
                description="Employee updated successfully",
                schema=EmployeeSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Employee not found")
        },
        tags=["Employees"]
    )
    def update(self, request, *args, **kwargs):
        """Update an employee object based on user group and company (PUT)."""
        instance = self.get_object()

        # Ensure the user and employee are in the same company
        if instance.user.company.id != request.user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Allow full update regardless of user group
        serializer = self.get_serializer(instance, data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Employee updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except ObjectDoesNotExist:
            return error_response("Employee not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while updating employee.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Partial Update Employee",
        operation_description="Partially update an existing employee's details. This is a partial update (PATCH).",
        request_body=EmployeeSerializer,
        responses={
            200: openapi.Response(
                description="Employee partially updated successfully",
                schema=EmployeeSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Employee not found")
        },
        tags=["Employees"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update an employee object based on user group and company (PATCH)."""
        instance = self.get_object()

        # Ensure the user and employee are in the same company
        if instance.user.company.id != request.user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Check user group and apply allowed fields
        if request.user.groups.filter(name='stuff').exists():
            allowed_fields = ['contact_number', 'date_of_joining']
            data = {key: value for key, value in request.data.items() if key in allowed_fields}

            if not data:
                return error_response("No valid fields to update for your group.", 
                                      error_type="ValidationError", 
                                      status_code=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance.user, data=data, partial=True)

        elif request.user.groups.filter(name='hr').exists():
            allowed_fields = ['employee_id']
            data = {key: value for key, value in request.data.items() if key in allowed_fields}

            if not data:
                return error_response("No valid fields to update for your group.", 
                                      error_type="ValidationError", 
                                      status_code=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance, data=data, partial=True)

        else:
            serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Employee partially updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except ObjectDoesNotExist:
            return error_response("Employee not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while partially updating employee.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Delete Employee",
        operation_description="Delete an employee.",
        responses={
            204: openapi.Response(description="Employee deleted successfully"),
            404: openapi.Response(description="Employee not found"),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Employees"]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an employee and return a success message."""
        try:
            instance = self.get_object()
            
            # Check if the request user's company matches the instance's company
            if instance.user.company.id != request.user.company.id:
                return error_response("You do not belong to the same company.", 
                                    error_type="PermissionDenied", 
                                    status_code=status.HTTP_403_FORBIDDEN)

            # Perform the delete operation
            self.perform_destroy(instance)
            return success_response(f"Employee {instance.employee_id} deleted successfully.")
        except NotFound:
            return error_response("Employee not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while deleting employee.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

# ViewSet for AttendanceLog
class AttendanceLogViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceLogSerializer
    queryset = AttendanceLog.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter attendance logs by the logged-in user's company.
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

# ViewSet for Shift
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

# ViewSet for Schedule
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

# ViewSet for WorkHours
class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
