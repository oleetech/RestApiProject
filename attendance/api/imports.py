# imports.py

# Django imports
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# DRF imports
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle

# drf_yasg imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Custom imports (adjust as needed for your project)
from .utils import success_response, error_response, validation_error_response
from .permission import AttendanceHasDynamicModelPermission
from ..models import Employee, Device, AttendanceLog, Shift, Schedule, WorkHours
from .serializers import (
    EmployeeSerializer,
    DeviceSerializer,
    AttendanceLogSerializer,
    ShiftSerializer,
    ScheduleSerializer,
    WorkHoursSerializer,
)
