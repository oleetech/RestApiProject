
from ..imports import *
class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,AttendanceHasDynamicModelPermission]
    @swagger_auto_schema(
        operation_summary="List Attendance Logs",
        operation_description="Retrieve a list of attendance logs for the user's company.",
        responses={
            200: openapi.Response(
                description="A list of attendance logs",
                schema=AttendanceLogSerializer(many=True)
            ),
            403: openapi.Response(
                description="Permission denied"
            )
        },
        tags=["Attendance Logs"]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of attendance logs for the user's company."""
        try:
            # Filter to get attendance logs belonging to the user's company
            queryset = self.get_queryset().filter(company=request.user.company)

            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"detail": "Attendance logs retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No attendance logs found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": "Database error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Create Attendance Log",
        operation_description="Create a new attendance log.",
        request_body=AttendanceLogSerializer,
        responses={
            201: openapi.Response(
                description="Attendance log created successfully",
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
        },
        tags=["Attendance Logs"]
    )
    def create(self, request, *args, **kwargs):
        """Custom create function for attendance log."""
        user = request.user
        
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি লগ প্রদান করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"detail": "Attendance log created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": "Validation error.", "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": "Server error while creating attendance log.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Save the user and their company when creating attendance log."""
        serializer.save()

    @swagger_auto_schema(
        operation_summary="Retrieve Attendance Log",
        operation_description="Retrieve a specific attendance log.",
        responses={
            200: openapi.Response(
                description="Attendance log details retrieved successfully",
                schema=AttendanceLogSerializer()
            ),
            404: openapi.Response(description="Attendance log not found"),
            403: openapi.Response(description="Permission denied"),
        },
        tags=["Attendance Logs"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Return a single attendance log object."""
        try:
            instance = self.get_object()
            if instance.company.id != request.user.company.id:
                return Response({"detail": "You do not have permission to access this attendance log."}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(instance)
            return Response({"detail": "Attendance log retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": "Attendance log not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": "Database error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Retrieve Attendance Logs by Employee ID",
        operation_description="Retrieve attendance logs for a specific employee by their ID.",
        manual_parameters=[
            openapi.Parameter(
                'employee_id',
                openapi.IN_QUERY,
                description="ID of the employee whose attendance logs you want to retrieve.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Attendance logs retrieved successfully",
                schema=AttendanceLogSerializer(many=True)
            ),
            400: openapi.Response(description="employee_id parameter is required."),
            404: openapi.Response(description="Employee not found or does not belong to your company."),
            403: openapi.Response(description="Permission denied"),
        },
        tags=["Attendance Logs"]
    )
    @action(detail=False, methods=['get'], url_path='logs-by-employee/(?P<employee_id>[^/.]+)')  # Updated URL path
    def get_logs_by_employee(self, request, employee_id=None):
        if not employee_id:
            return Response({"error": "employee_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter logs by the employee_id
            logs = AttendanceLog.objects.filter(employee_id=employee_id)  # Use a valid field
            serializer = AttendanceLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttendanceLog.DoesNotExist:
            return Response({"error": "No logs found for this employee."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Update Attendance Log",
        operation_description="Update an existing attendance log.",
        request_body=AttendanceLogSerializer,
        responses={
            200: openapi.Response(
                description="Attendance log updated successfully",
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Attendance log not found"),
        },
        tags=["Attendance Logs"]
    )
    def update(self, request, *args, **kwargs):
        """Update an existing attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": "You do not have permission to update this attendance log."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = self.get_serializer(instance, data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"detail": "Attendance log updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": "Validation error.", "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": "Attendance log not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": "Server error while updating attendance log.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Partial Update Attendance Log",
        operation_description="Partially update an existing attendance log.",
        request_body=AttendanceLogSerializer,
        responses={
            200: openapi.Response(
                description="Attendance log partially updated successfully",
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Attendance log not found"),
        },
        tags=["Attendance Logs"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update an attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": "You do not have permission to partially update this attendance log."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"detail": "Attendance log partially updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": "Validation error.", "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": "Attendance log not found."}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": "Server error while partially updating attendance log.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete Attendance Log",
        operation_description="Delete an existing attendance log.",
        responses={
            204: openapi.Response(description="Attendance log deleted successfully"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Attendance log not found"),
        },
        tags=["Attendance Logs"]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": "You do not have permission to delete this attendance log."}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({"detail": "Attendance log deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

