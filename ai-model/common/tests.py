"""Test untuk utilitas bersama dan format error API."""

from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ErrorFormatTests(APITestCase):
    """Semua error harus memakai format `{"error": {...}}`."""

    def test_not_found_uses_consistent_error_shape(self):
        """Endpoint yang tidak ada menghasilkan format error yang seragam."""
        response = self.client.get("/api/v1/tidak-ada/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = response.json()
        self.assertIn("error", body)
        self.assertIn("code", body["error"])
        self.assertIn("message", body["error"])

    def test_error_response_does_not_leak_stack_trace(self):
        """Respons error tidak boleh memuat detail internal."""
        response = self.client.get("/api/v1/tidak-ada/")

        body = str(response.json()).lower()
        self.assertNotIn("traceback", body)
        self.assertNotIn("django", body)


class ApiIndexTests(APITestCase):
    """Indeks API."""

    def test_index_lists_endpoints(self):
        """Indeks API mencantumkan endpoint yang tersedia."""
        response = self.client.get(reverse("api-index"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["version"], "v1")
        self.assertEqual(
            response.data["endpoints"]["analysis"]["create"], "/api/v1/analyses/"
        )


class ApiPathTests(APITestCase):
    """Cek path endpoint sesuai kontrak di `docs/api.md`.

    Test ini sengaja memakai path literal, bukan hanya `reverse()`, supaya
    salah prefix pada `include()` langsung ketahuan.
    """

    DOCUMENTED_PATHS = {
        "auth-register": "/api/v1/auth/register/",
        "auth-login": "/api/v1/auth/login/",
        "auth-logout": "/api/v1/auth/logout/",
        "auth-me": "/api/v1/auth/me/",
        "crop-list": "/api/v1/crops/",
        "disease-list": "/api/v1/diseases/",
        "resource-list": "/api/v1/resources/",
        "analysis-list": "/api/v1/analyses/",
        "api-index": "/api/v1/",
    }

    def test_documented_paths_resolve_to_expected_url(self):
        """Setiap endpoint harus berada pada path yang didokumentasikan."""
        for name, expected_path in self.DOCUMENTED_PATHS.items():
            with self.subTest(endpoint=name):
                self.assertEqual(reverse(name), expected_path)

    def test_register_endpoint_is_reachable_by_literal_path(self):
        """Pendaftaran harus bisa dipanggil memakai path literal."""
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "petani_literal",
                "email": "literal@example.com",
                "password": "RahasiaKuat123",
                "password_confirm": "RahasiaKuat123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
