from ..imports import *

# ViewSet for Device
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,AttendanceHasDynamicModelPermission]
    throttle_classes = [UserRateThrottle]

    @method_decorator(csrf_exempt)  # Disabling CSRF protection
    def dispatch(self, *args, **kwargs):
        # Add custom checks or logging here
        print(f"Request Method: {self.request.method} | Request Path: {self.request.path}")
        
        response = super().dispatch(*args, **kwargs)

        # Applying CSRF protection
        CsrfViewMiddleware().process_view(self.request, None, (), {})

        return response
        
            
    @swagger_auto_schema(
        operation_summary="List Devices",
        operation_description="Retrieve a list of devices belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="A list of devices",
                schema=DeviceSerializer(many=True)
            ),
            403: openapi.Response(
                description="Permission denied"
            )
        },
        tags=["Devices"]
    )
    def list(self, request, *args, **kwargs):
        """Return an array of device objects belonging to the request user's company."""
        try:
            # Filter the queryset to get only devices of the user's company
            queryset = self.get_queryset().filter(company=request.user.company)

            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return success_response("Device list retrieved successfully.", serializer.data)
            else:
                return success_response("No devices found.", [])
        except DatabaseError as e:
            return error_response("Database error occurred.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Retrieve Device",
        operation_description="Retrieve details of a single device belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="Device details retrieved successfully",
                schema=DeviceSerializer()
            ),
            404: openapi.Response(description="Device not found"),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Devices"]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single device object that belongs to the request user's company.
        Ensures the user has the appropriate permission to access the device.
        """
        try:
            # Get the device instance using the primary key
            instance = self.get_object()

            # Check if the device belongs to the same company as the user
            if instance.company.id != request.user.company.id:
                return error_response(
                    "You do not have permission to access this device.",
                    error_type="PermissionDenied",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            # Serialize the device data if the company check passes
            serializer = self.get_serializer(instance)
            return success_response(
                f"Device {instance.device_id} details retrieved successfully.",
                serializer.data
            )

        except NotFound:
            # Handle case where device is not found
            return error_response(
                "Device not found.",
                error_type="NotFoundError",
                status_code=status.HTTP_404_NOT_FOUND
            )

        except DatabaseError as e:
            # Handle any database-related errors
            return error_response(
                "A database error occurred while retrieving the device.",
                str(e),
                error_type="ServerError",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_summary="Create Device",
        operation_description="Create a new device for the logged-in user and return the created device object.",
        request_body=DeviceSerializer,
        responses={
            201: openapi.Response(
                description="Device created successfully",
                schema=DeviceSerializer()
            ),
            400: openapi.Response(
                description="Validation error occurred."
            ),
        },
        tags=["Devices"]
    )
    def create(self, request, *args, **kwargs):
        """Create a new device and return the created object."""
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                return success_response("Device created successfully.", serializer.data, status_code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return validation_error_response(e.detail)
        except DatabaseError as e:
            return error_response("Server error while creating device.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update Device",
        operation_description="Update an existing device's details. This is a full update (PUT).",
        request_body=DeviceSerializer,
        responses={
            200: openapi.Response(
                description="Device updated successfully",
                schema=DeviceSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Device not found")
        },
        tags=["Devices"]
    )
    def update(self, request, *args, **kwargs):
        """Update a device object based on user group and company (PUT)."""
        instance = self.get_object()

        # Ensure the user and device are in the same company
        if instance.company.id != request.user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Allow full update regardless of user group
        serializer = self.get_serializer(instance, data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Device updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except NotFound:
            return error_response("Device not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while updating device.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Partial Update Device",
        operation_description="Partially update an existing device's details. This is a partial update (PATCH).",
        request_body=DeviceSerializer,
        responses={
            200: openapi.Response(
                description="Device partially updated successfully",
                schema=DeviceSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Device not found")
        },
        tags=["Devices"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a device object based on user group and company (PATCH)."""
        instance = self.get_object()

        # Ensure the user and device are in the same company
        if instance.company.id != request.user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Check user group and apply allowed fields
        allowed_fields = ['location', 'description', 'ip_address', 'last_sync_time']
        data = {key: value for key, value in request.data.items() if key in allowed_fields}

        if not data:
            return error_response("No valid fields to update.", 
                                  error_type="ValidationError", 
                                  status_code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=data, partial=True)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Device partially updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except NotFound:
            return error_response("Device not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while partially updating device.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete Device",
        operation_description="Delete a device.",
        responses={
            204: openapi.Response(description="Device deleted successfully"),
            404: openapi.Response(description="Device not found"),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Devices"]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a device and return a success message."""
        try:
            instance = self.get_object()

            # Check if the request user's company matches the instance's company
            if instance.company.id != request.user.company.id:
                return error_response("You do not belong to the same company.", 
                                    error_type="PermissionDenied", 
                                    status_code=status.HTTP_403_FORBIDDEN)

            # Perform the delete operation
            self.perform_destroy(instance)
            return success_response(f"Device {instance.device_id} deleted successfully.")
        except NotFound:
            return error_response("Device not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while deleting device.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
