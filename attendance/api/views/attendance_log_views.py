from ..imports import *
from django.utils.translation import gettext_lazy as _  # Importing translation functions

@method_decorator(csrf_protect, name='dispatch')
class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AttendanceHasDynamicModelPermission]
    throttle_classes = [UserRateThrottle]



    @swagger_auto_schema(
        operation_summary=_("List Attendance Logs"),
        operation_description=_("Retrieve a list of attendance logs for the user's company."),
        responses={
            200: openapi.Response(
                description=_("A list of attendance logs"),
                schema=AttendanceLogSerializer(many=True)
            ),
            403: openapi.Response(
                description=_("Permission denied")
            )
        },
        tags=[_("Attendance Logs")]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of attendance logs for the user's company."""
        try:
            # Filter to get attendance logs belonging to the user's company
            queryset = self.get_queryset().filter(company=request.user.company)

            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"detail": _("Attendance logs retrieved successfully."), "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": _("No attendance logs found.")}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": _("Database error occurred."), "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary=_("Create Attendance Log"),
        operation_description=_("Create a new attendance log."),
        request_body=AttendanceLogSerializer,
        responses={
            201: openapi.Response(
                description=_("Attendance log created successfully"),
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description=_("Validation error")),
            403: openapi.Response(description=_("Permission denied")),
        },
        tags=[_("Attendance Logs")]
    )

    @method_decorator(csrf_protect)  # CSRF সুরক্ষা সক্রিয় করা
    def create(self, request, *args, **kwargs):
        """Custom create function for attendance log."""
        user = request.user
        
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": _("You or your company is inactive, and attendance logs cannot be submitted.")},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"detail": _("Attendance log created successfully."), "data": serializer.data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": _("Validation error."), "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            return Response({"detail": _("Server error while creating attendance log."), "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Save the user and their company when creating attendance log."""
        serializer.save()

    @swagger_auto_schema(
        operation_summary=_("Retrieve Attendance Log"),
        operation_description=_("Retrieve a specific attendance log."),
        responses={
            200: openapi.Response(
                description=_("Attendance log details retrieved successfully"),
                schema=AttendanceLogSerializer()
            ),
            404: openapi.Response(description=_("Attendance log not found")),
            403: openapi.Response(description=_("Permission denied")),
        },
        tags=[_("Attendance Logs")]
    )
    @method_decorator(csrf_protect)  # CSRF সুরক্ষা সক্রিয় করা
    def retrieve(self, request, *args, **kwargs):
        """Return a single attendance log object."""
        try:
            instance = self.get_object()
            if instance.company.id != request.user.company.id:
                return Response({"detail": _("You do not have permission to access this attendance log.")}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(instance)
            return Response({"detail": _("Attendance log retrieved successfully."), "data": serializer.data}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": _("Attendance log not found.")}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": _("Database error occurred."), "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary=_("Retrieve Attendance Logs by Employee ID"),
        operation_description=_("Retrieve attendance logs for a specific employee by their ID."),
        manual_parameters=[
            openapi.Parameter(
                'employee_id',
                openapi.IN_QUERY,
                description=_("ID of the employee whose attendance logs you want to retrieve."),
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description=_("Attendance logs retrieved successfully"),
                schema=AttendanceLogSerializer(many=True)
            ),
            400: openapi.Response(description=_("employee_id parameter is required.")),
            404: openapi.Response(description=_("Employee not found or does not belong to your company.")),
            403: openapi.Response(description=_("Permission denied")),
        },
        tags=[_("Attendance Logs")]
    )
    @action(detail=False, methods=['get'], url_path='logs-by-employee/(?P<employee_id>[^/.]+)')  # Updated URL path
    @method_decorator(csrf_protect)  # CSRF সুরক্ষা সক্রিয় করা

    def get_logs_by_employee(self, request, employee_id=None):
        if not employee_id:
            return Response({"error": _("employee_id parameter is required.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter logs by the employee_id
            logs = AttendanceLog.objects.filter(employee_id=employee_id)  # Use a valid field
            serializer = AttendanceLogSerializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttendanceLog.DoesNotExist:
            return Response({"error": _("No logs found for this employee.")}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary=_("Update Attendance Log"),
        operation_description=_("Update an existing attendance log."),
        request_body=AttendanceLogSerializer,
        responses={
            200: openapi.Response(
                description=_("Attendance log updated successfully"),
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description=_("Validation error")),
            403: openapi.Response(description=_("Permission denied")),
            404: openapi.Response(description=_("Attendance log not found")),
        },
        tags=[_("Attendance Logs")]
    )
    @method_decorator(csrf_protect)  # CSRF সুরক্ষা সক্রিয় করা
    def update(self, request, *args, **kwargs):
        """Update an existing attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": _("You do not have permission to update this attendance log.")}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = self.get_serializer(instance, data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"detail": _("Attendance log updated successfully."), "data": serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": _("Validation error."), "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": _("Attendance log not found.")}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": _("Server error while updating attendance log."), "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary=_("Partial Update Attendance Log"),
        operation_description=_("Partially update an existing attendance log."),
        request_body=AttendanceLogSerializer,
        responses={
            200: openapi.Response(
                description=_("Attendance log partially updated successfully"),
                schema=AttendanceLogSerializer()
            ),
            400: openapi.Response(description=_("Validation error")),
            403: openapi.Response(description=_("Permission denied")),
            404: openapi.Response(description=_("Attendance log not found")),
        },
        tags=[_("Attendance Logs")]
    )
    @method_decorator(csrf_protect)  # CSRF protection enabled
    def partial_update(self, request, *args, **kwargs):
        """Partially update an attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": _("You do not have permission to partially update this attendance log.")}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"detail": _("Attendance log partially updated successfully."), "data": serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": _("Validation error."), "error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": _("Attendance log not found.")}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return Response({"detail": _("Server error while partially updating attendance log."), "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary=_("Delete Attendance Log"),
        operation_description=_("Delete an attendance log."),
        responses={
            204: openapi.Response(description=_("Attendance log deleted successfully")),
            404: openapi.Response(description=_("Attendance log not found")),
            403: openapi.Response(description=_("Permission denied")),
        },
        tags=[_("Attendance Logs")]
    )
    @method_decorator(csrf_protect)  # CSRF সুরক্ষা সক্রিয় করা
    def destroy(self, request, *args, **kwargs):
        """Delete an attendance log."""
        instance = self.get_object()

        if instance.company.id != request.user.company.id:
            return Response({"detail": _("You do not have permission to delete this attendance log.")}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({"detail": _("Attendance log deleted successfully.")}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """Delete the attendance log instance."""
        instance.delete()
