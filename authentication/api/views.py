from rest_framework import status, viewsets

from django.contrib.auth import authenticate, login,logout
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import PermissionDenied  
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from django.utils.translation import gettext as _
from .serializers import CompanySerializer,RegisterSerializer
from .permissions import DynamicModelLevelPermission,DynamicObjectLevelPermission
from .utils import success_response, error_response, validation_error_response

from ..models import Company
@method_decorator(csrf_protect, name='dispatch')
class CompanyView(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing company instances.
    """
    permission_classes = [IsAuthenticated, DynamicModelLevelPermission,DynamicObjectLevelPermission]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]  

    def list(self, request):
        """
        List all companies.
        """
        try:
            companies = Company.get_all_companies(request.user)
            serializer = self.get_serializer(companies, many=True)
            return success_response("Companies retrieved successfully", data=serializer.data)

        except PermissionDenied as e:
            return error_response("You do not have permission to view companies", details=str(e), error_type="PermissionDenied")

    def retrieve(self, request, pk=None):
        """
        Retrieve a single company by its ID.
        """
        try:
            company = Company.get_company(request.user, pk)
        except ValueError as e:
            return error_response("Company not found", details=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return error_response("You do not have permission to view this company", details=str(e), error_type="PermissionDenied")

        serializer = self.get_serializer(company)
        return success_response("Company retrieved successfully", data=serializer.data)

    def create(self, request):
        """
        Create a new company if the user has the necessary permissions.
        """
        try:
            # Call the model's create method
            company = Company.create_company(request.user, **request.data)
        except PermissionDenied as e:
            return error_response("You do not have permission to add a company", details=str(e), error_type="PermissionDenied")
        except Exception as e:
            return error_response("Error creating company", details=str(e))

        serializer = CompanySerializer(company)
        return success_response("Company created successfully", data=serializer.data, status_code=status.HTTP_201_CREATED)



    def destroy(self, request, pk=None):
        company = self.get_object()  
        try:
            Company.delete_company(request.user, company)
        except PermissionDenied as e:
            return error_response("You do not have permission to delete this company", details=str(e), error_type="PermissionDenied")
        except Exception as e:
            return error_response("Error deleting company", details=str(e))

        return success_response("Company deleted successfully", status_code=status.HTTP_204_NO_CONTENT)

# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]  
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": _("Email and password are required.")}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Generate Refresh Token and Access Token
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Optionally add extra data to the access token
            access['email'] = user.email
            access['username'] = user.username
            access['user_id'] = user.id

            # Prepare the response with the tokens
            response = Response({
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'id': user.id,
                },
                'access': str(access),  # Send access token in the response
            }, status=status.HTTP_200_OK)

            # Set the refresh token in an HttpOnly cookie
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),  # Save the refresh token as a string
                httponly=True,  # Prevent JavaScript access
                secure=True,  # Only send over HTTPS
                samesite='Strict',  # Prevent CSRF attacks
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()  # Set token expiry
            )

            return response

        return Response({"error": _("Invalid credentials.")}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        try:
            # Get the refresh token from the cookie
            refresh_token = request.COOKIES.get("refresh_token")  # 'refresh_token' হচ্ছে কুকির নাম

            if not refresh_token:
                return Response({"error": "Refresh token not found in cookies."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()  # ব্ল্যাকলিস্ট করা হচ্ছে
            
            # Logout from Django session
            logout(request)  # Django সেশনে লগ আউট করা হচ্ছে

            # Optionally, delete the cookie from the response
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token")  # কুকি মুছে ফেলা হচ্ছে
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Refresh token থেকে এক্সেস টোকেন তৈরি
class RefreshTokenView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token not found."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)

            return Response({
                'access': new_access_token
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)