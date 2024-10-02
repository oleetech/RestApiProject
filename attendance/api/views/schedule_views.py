# Import everything from your centralized imports module
from ..imports import *  # Assuming you have a centralized imports module

# ViewSet for Schedule
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
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