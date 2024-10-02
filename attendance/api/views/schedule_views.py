# Import everything from your centralized imports module
from ..imports import *  # Assuming you have a centralized imports module

# ViewSet for Schedule
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]