# Import everything from your imports module
from ..imports import *  # Assuming you have a centralized imports module


# ViewSet for Shift
class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
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
        operation_summary="List Shifts",
        operation_description="Retrieve a list of shifts belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="A list of shifts",
                schema=ShiftSerializer(many=True)
            ),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Shifts"]
    )
    def list(self, request, *args, **kwargs):
        """Return a list of shift objects belonging to the request user's company."""
        user = request.user
        try:
            # Check if user's company and user are active
            if not user.company.is_active or not user.is_active:
                return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

            # Filter the shifts by user's company
            queryset = self.get_queryset().filter(company=user.company)

            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return success_response("Shift list retrieved successfully.", serializer.data)
            else:
                return success_response("No shifts found.", [])
        except DatabaseError as e:
            return error_response("Database error occurred.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Retrieve Shift",
        operation_description="Retrieve details of a single shift belonging to the user's company.",
        responses={
            200: openapi.Response(
                description="Shift details retrieved successfully",
                schema=ShiftSerializer()
            ),
            404: openapi.Response(description="Shift not found"),
            403: openapi.Response(description="Permission denied")
        },
        tags=["Shifts"]
    )
    def retrieve(self, request, *args, **kwargs):
        """Return a single shift object belonging to the request user's company."""
        user = request.user
        try:
            # Get the shift instance
            instance = self.get_object()

            # Check if the shift's company matches the user's company
            if instance.company.id != user.company.id:
                return error_response("You do not have permission to access this shift.", 
                                      error_type="PermissionDenied", 
                                      status_code=status.HTTP_403_FORBIDDEN)

            # Check if user's company and user are active
            if not user.company.is_active or not user.is_active:
                return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

            # Serialize the shift details
            serializer = self.get_serializer(instance)
            return success_response(f"Shift {instance.name} details retrieved.", serializer.data)

        except NotFound:
            return error_response("Shift not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Database error occurred.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Create Shift",
        operation_description="Create a new shift for the user's company.",
        request_body=ShiftSerializer,
        responses={
            201: openapi.Response(
                description="Shift created successfully",
                schema=ShiftSerializer()
            ),
            400: openapi.Response(description="Validation error")
        },
        tags=["Shifts"]
    )
    def create(self, request, *args, **kwargs):
        """Create a new shift for the user's company."""
        user = request.user

        # Check if user's company and user are active
        if not user.company.is_active or not user.is_active:
            return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                # Set the company to the current user's company
                serializer.save(company=user.company)
                return success_response("Shift created successfully.", serializer.data, status_code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return validation_error_response(e.detail)
        except DatabaseError as e:
            return error_response("Server error while creating shift.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update Shift",
        operation_description="Update an existing shift's details.",
        request_body=ShiftSerializer,
        responses={
            200: openapi.Response(
                description="Shift updated successfully",
                schema=ShiftSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Shift not found")
        },
        tags=["Shifts"]
    )
    def update(self, request, *args, **kwargs):
        """Update a shift for the user's company (PUT)."""
        user = request.user
        instance = self.get_object()

        # Ensure the shift belongs to the same company as the user
        if instance.company.id != user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Check if user's company and user are active
        if not user.company.is_active or not user.is_active:
            return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Shift updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except ObjectDoesNotExist:
            return error_response("Shift not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while updating shift.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        operation_summary="Partial Update Shift",
        operation_description="Partially update an existing shift's details. This is a partial update (PATCH).",
        request_body=ShiftSerializer,
        responses={
            200: openapi.Response(
                description="Shift partially updated successfully",
                schema=ShiftSerializer()
            ),
            400: openapi.Response(description="Validation error"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Shift not found")
        },
        tags=["Shifts"]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a shift object based on user group and company (PATCH)."""
        user = request.user
        instance = self.get_object()

        # Ensure the user and shift are in the same company
        if instance.user.company.id != user.company.id:
            return error_response("You do not belong to the same company.", 
                                error_type="PermissionDenied", 
                                status_code=status.HTTP_403_FORBIDDEN)

        # Check if user's company and user are active
        if not user.company.is_active or not user.is_active:
            return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_update(serializer)
                return success_response("Shift partially updated successfully.", serializer.data)

        except ValidationError as e:
            return validation_error_response(e.detail)
        except ObjectDoesNotExist:
            return error_response("Shift not found.", error_type="NotFoundError", status_code=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            return error_response("Server error while partially updating shift.", str(e), error_type="ServerError", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete Shift",
        operation_description="Delete a shift belonging to the user's company.",
        responses={
            204: openapi.Response(description="Shift deleted successfully"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Shift not found")
        },
        tags=["Shifts"]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a shift object for the user's company."""
        user = request.user
        instance = self.get_object()

        # Ensure the shift belongs to the same company as the user
        if instance.company.id != user.company.id:
            return error_response("You do not belong to the same company.", 
                                  error_type="PermissionDenied", 
                                  status_code=status.HTTP_403_FORBIDDEN)

        # Check if user's company and user are active
        if not user.company.is_active or not user.is_active:
            return error_response("Your company or account is inactive.", error_type="PermissionDenied", status_code=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return success_response("Shift deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)

