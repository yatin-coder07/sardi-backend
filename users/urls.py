from django.urls import path
from .views import GoogleAuthView, UserDetailView

urlpatterns = [
    path("google/", GoogleAuthView.as_view(), name="google-login"),
    path("user/",UserDetailView.as_view(), name="user-detail")
]