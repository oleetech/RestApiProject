from django.urls import path
from .views import RegisterView, LoginView, LogoutView,RefreshTokenView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),  # Custom login route
    path('auth/logout/', LogoutView.as_view(), name='logout'),  # Logout route
    path('auth/refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),  # New refresh token route

]
