"""Endpoint autentikasi dan profil pengguna.

Mekanisme autentikasi memakai token DRF (`rest_framework.authtoken`). Token
disimpan di server dan dikirim klien pada header `Authorization: Token
<token>`. Ini dipilih karena lebih mudah diintegrasikan dengan Flutter
daripada session + CSRF, dan tidak memakai cookie yang dapat dikirim
otomatis ke server lain.
"""

from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
    """Daftarkan akun baru."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Buat pengguna dan kembalikan token."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Tukar username dan password menjadi token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Autentikasi pengguna dan kembalikan token."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "error": {
                        "code": "invalid_request",
                        "message": "Username dan password wajib diisi.",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Username atau password salah.",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
            }
        )


class LogoutView(APIView):
    """Akhiri sesi dengan mencabut token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Cabut token milik pengguna yang sedang masuk."""
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Tampilkan profil pengguna yang sedang masuk."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Kembalikan data pengguna beserta profilnya."""
        return Response(UserSerializer(request.user).data)
