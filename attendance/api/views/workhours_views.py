# Import everything from your centralized imports module
from ..imports import *  # Assuming you have a centralized imports module
# ViewSet for WorkHours
class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]