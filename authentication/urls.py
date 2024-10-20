# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/update/', views.update_profile, name='update_profile'),
]
