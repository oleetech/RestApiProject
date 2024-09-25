from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Custom function to generate tokens for the user
def get_tokens_for_user(user):
    """
    Custom method to generate tokens (refresh and access) for a given user,
    and include extra fields in the token payload like email, username, and mobileNo.
    """
    refresh = RefreshToken.for_user(user)

    # Add custom fields to the access token
    refresh['email'] = user.email  # Add user's email to the token
    refresh['username'] = user.username  # Add user's username to the token

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        # Optionally, include user data in the response
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
        }
    }



class LoginView(APIView):
    """
    Custom login view to authenticate the user and return JWT tokens securely.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Generate JWT tokens
            tokens = get_tokens_for_user(user)

            # Set refresh token in a secure HTTP-only cookie
            response = Response({
                'user': tokens['user'],  # Include user details in response
                'access': tokens['access'],  # Send access token in the response
            }, status=status.HTTP_200_OK)

            # Set the refresh token in an HttpOnly cookie
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,  # Prevent JavaScript access
                secure=True,  # Only send over HTTPS
                samesite='Strict',  # Prevent CSRF
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()  # Set token expiry
            )

            return response

        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
# Logout View
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


