from django.urls import path
from .views import GoogleAuthView, UserDetailView , FixAdminsView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("google/", GoogleAuthView.as_view(), name="google-login"),
    path("user/",UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
  
]