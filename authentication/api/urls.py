from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, RefreshTokenView, CompanyView

router = DefaultRouter()
router.register(r'companies', CompanyView, basename='company')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),  # REST API logout
    path('auth/refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
    path('', include(router.urls)),  
]
