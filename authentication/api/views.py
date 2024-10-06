from rest_framework import status
from django.contrib.auth import authenticate, login
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.translation import gettext as _
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