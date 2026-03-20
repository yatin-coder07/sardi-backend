from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import traceback  # ✅ important

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import GoogleAuthSerializer
from users.models import User


class GoogleAuthView(APIView):
    permission_classes = []  # public

    def post(self, request):
        try:
            print("📥 Incoming request data:", request.data)

            # ✅ Validate input
            serializer = GoogleAuthSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            token = serializer.validated_data["token"]
            print("🔑 Token received:", token[:30], "...")  # partial log

            # ✅ Get client ID
            GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
            print("🆔 GOOGLE_CLIENT_ID:", GOOGLE_CLIENT_ID)

            if not GOOGLE_CLIENT_ID:
                return Response(
                    {"error": "Google Client ID not configured"},
                    status=500
                )

            # ✅ Verify Google token
            try:
                google_user = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    GOOGLE_CLIENT_ID
                )
                print("✅ Google user verified:", google_user)

            except Exception as e:
                print("❌ GOOGLE VERIFY ERROR:", str(e))
                traceback.print_exc()  # full stack trace
                return Response(
                    {"error": f"Google verification failed: {str(e)}"},
                    status=400
                )

            # ✅ Extract data
            email = google_user.get("email")
            username = google_user.get("name", "")
            picture = google_user.get("picture", "")
            oauth_id = google_user.get("sub")

            print("👤 Extracted:", email, username)

            if not email:
                return Response({"error": "Email not available"}, status=400)

            # ✅ SAFE USER CREATION (better than get_or_create)
            try:
                user = User.objects.filter(email=email).first()

                if not user:
                    user = User.objects.create(
                        email=email,
                        username=username or email,
                        oauth_provider="google",
                        oauth_id=oauth_id,
                        profile_picture=picture,
                    )
                    print("🆕 User created:", user.id)

                else:
                    user.username = username
                    user.profile_picture = picture
                    user.save()
                    print("♻️ User updated:", user.id)

            except Exception as e:
                print("❌ USER CREATION ERROR:", str(e))
                traceback.print_exc()
                return Response(
                    {"error": f"User creation failed: {str(e)}"},
                    status=500
                )

            # ✅ Generate tokens
            try:
                refresh = RefreshToken.for_user(user)
                print("🔐 Tokens generated")

            except Exception as e:
                print("❌ TOKEN ERROR:", str(e))
                traceback.print_exc()
                return Response(
                    {"error": f"Token generation failed: {str(e)}"},
                    status=500
                )

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

        except Exception as e:
            print("💥 UNEXPECTED ERROR:", str(e))
            traceback.print_exc()
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=500
            )