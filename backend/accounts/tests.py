"""Test untuk endpoint autentikasi dan profil."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import Profile


class RegisterTests(APITestCase):
    """Pendaftaran akun baru."""

    def test_register_creates_user_profile_and_token(self):
        """Pendaftaran membuat user, profil, dan token sekaligus."""
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "petani1",
                "email": "petani1@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaKuat123",
                "display_name": "Pak Budi",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

        user = User.objects.get(username="petani1")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(Token.objects.filter(user=user).exists())
        self.assertEqual(response.data["user"]["profile"]["role"], Profile.Role.FARMER)

    def test_password_is_not_returned(self):
        """Password tidak boleh ikut ke respons."""
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "petani2",
                "email": "petani2@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaKuat123",
            },
            format="json",
        )

        self.assertNotIn("password", response.data["user"])

    def test_password_is_hashed_in_database(self):
        """Password harus disimpan sebagai hash, bukan teks biasa."""
        self.client.post(
            reverse("auth-register"),
            {
                "username": "petani3",
                "email": "petani3@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaKuat123",
            },
            format="json",
        )

        user = User.objects.get(username="petani3")
        self.assertNotEqual(user.password, "RahasiaKuat123")
        self.assertTrue(user.password.startswith("pbkdf2_"))

    def test_mismatched_password_is_rejected(self):
        """Konfirmasi password yang tidak cocok harus ditolak."""
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "petani4",
                "email": "petani4@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaBerbeda123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")
        self.assertFalse(User.objects.filter(username="petani4").exists())

    def test_weak_password_is_rejected(self):
        """Password lemah harus ditolak oleh validator Django."""
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "petani5",
                "email": "petani5@example.com",
                "password": "12345",
                "password_confirm": "12345",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="petani5").exists())

    def test_duplicate_email_is_rejected(self):
        """Email ganda harus ditolak."""
        User.objects.create_user(
            username="sudah", email="ganda@example.com", password="RahasiaKuat123"
        )

        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "petani6",
                "email": "ganda@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaKuat123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error"]["details"])


class LoginLogoutTests(APITestCase):
    """Login, profil, dan logout."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="petani", email="petani@example.com", password="RahasiaKuat123"
        )

    def test_login_returns_token(self):
        """Login yang benar mengembalikan token."""
        response = self.client.post(
            reverse("auth-login"),
            {"username": "petani", "password": "RahasiaKuat123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_with_wrong_password_is_rejected(self):
        """Password salah harus ditolak tanpa membocorkan informasi."""
        response = self.client.post(
            reverse("auth-login"),
            {"username": "petani", "password": "SalahSekali123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"]["code"], "invalid_credentials")

    def test_login_without_credentials_is_rejected(self):
        """Kredensial kosong harus ditolak."""
        response = self.client.post(reverse("auth-login"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")

    def test_me_requires_authentication(self):
        """Endpoint profil harus menolak tamuel."""
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        """Profil mengembalikan data pengguna yang sedang masuk."""
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "petani")

    def test_logout_revokes_token(self):
        """Logout harus mencabut token."""
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post(reverse("auth-logout"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_token_authentication_works(self):
        """Token yang valid harus dipakai untuk mengakses endpoint terlindungi."""
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "petani")
