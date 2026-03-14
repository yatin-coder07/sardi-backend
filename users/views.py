from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import GoogleAuthSerializer
from users.models import User


from rest_framework.permissions import IsAuthenticated


class GoogleAuthView(APIView):

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            google_user = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response({"error": "Invalid token"}, status=400)

        email = google_user["email"]
        username = google_user.get("name")
        picture = google_user.get("picture")
        oauth_id = google_user["sub"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "oauth_provider": "google",
                "oauth_id": oauth_id,
                "profile_picture": picture,
            }
        )

        # Update picture or username if user already exists
        if not created:
            user.username = username
            user.profile_picture = picture
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture
        })
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)