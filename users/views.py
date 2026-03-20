from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
import os

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import GoogleAuthSerializer
from users.models import User
from rest_framework.permissions import IsAuthenticated


# 🔥 GOOGLE AUTH VIEW
class GoogleAuthView(APIView):
    permission_classes = []  # ✅ public route

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        # ✅ Get CLIENT ID from ENV (NOT settings hardcoded)
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

        if not GOOGLE_CLIENT_ID:
            return Response(
                {"error": "Google Client ID not configured"},
                status=500
            )

        try:
            google_user = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {"error": "Invalid or expired Google token"},
                status=400
            )

        # ✅ Extract user info safely
        email = google_user.get("email")
        username = google_user.get("name", "")
        picture = google_user.get("picture", "")
        oauth_id = google_user.get("sub")

        if not email:
            return Response({"error": "Email not available"}, status=400)

        # ✅ Create or update user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "oauth_provider": "google",
                "oauth_id": oauth_id,
                "profile_picture": picture,
            }
        )

        if not created:
            user.username = username
            user.profile_picture = picture
            user.save()

        # ✅ Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "is_staff": user.is_staff,
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })


# 🔥 USER DETAILS
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture,
            "is_staff": user.is_staff,
        })


# 🔥 LOGOUT
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )