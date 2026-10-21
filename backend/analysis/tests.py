"""Test untuk endpoint analisis gambar."""

from __future__ import annotations

import tempfile
from io import BytesIO
from unittest import mock

import requests

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from agriculture.models import Crop, Disease
from analysis.models import Analysis


def make_image_bytes(width: int = 300, height: int = 300, fmt: str = "PNG") -> BytesIO:
    """Buat berkas gambar di dalam memori untuk diunggah pada test."""
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(90, 150, 60)).save(buffer, format=fmt)
    buffer.seek(0)
    return buffer


class AnalysisPermissionTests(APITestCase):
    """Batas izin analisis."""

    def setUp(self):
        self.url = reverse("analysis-list")
        self.user = User.objects.create_user(username="petani", password="RahasiaKuat123")

    def test_list_requires_authentication(self):
        """Tanpa login, permintaan ditolak."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_own_records(self):
        """Pengguna tidak boleh melihat analisis orang lain."""
        other = User.objects.create_user(username="lain", password="RahasiaKuat123")
        Analysis.objects.create(user=other, status=Analysis.Status.COMPLETED)
        Analysis.objects.create(user=self.user, status=Analysis.Status.COMPLETED)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Analysis.objects.filter(user=self.user).count(), 1)

    def test_detail_of_other_user_is_not_found(self):
        """Record milik orang lain harus menghasilkan 404, bukan 403."""
        other = User.objects.create_user(username="lain", password="RahasiaKuat123")
        analysis = Analysis.objects.create(user=other, status=Analysis.Status.COMPLETED)

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("analysis-detail", args=[analysis.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnalysisUploadValidationTests(APITestCase):
    """Validasi berkas yang diunggah."""

    def setUp(self):
        self.user = User.objects.create_user(username="petani", password="RahasiaKuat123")
        self.client.force_authenticate(self.user)
        self.url = reverse("analysis-list")

    def test_non_image_file_is_rejected(self):
        """Berkas teks harus ditolak dengan kode error yang jelas."""
        response = self.client.post(
            self.url, {"image": _named_file("catatan.txt", b"bukan gambar")}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")
        self.assertIn("image", response.data["error"]["details"])

    def test_image_too_small_is_rejected(self):
        """Gambar beresolusi sangat kecil tidak berguna untuk analisis."""
        response = self.client.post(
            self.url, {"image": _named_file("kecil.png", _png_bytes(10, 10))}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")

    def test_file_larger_than_limit_is_rejected(self):
        """Berkas melebihi batas ukuran harus ditolak."""
        with override_settings(MAX_UPLOAD_SIZE_BYTES=1024):
            response = self.client.post(
                self.url,
                {"image": _named_file("besar.png", _png_bytes(2000, 2000))},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_image_is_rejected(self):
        """Gambar wajib diunggah."""
        response = self.client.post(self.url, {}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")

    def test_unknown_crop_is_rejected(self):
        """Kode tanaman yang tidak dikenal harus ditolak."""
        response = self.client.post(
            self.url,
            {
                "image": _named_file("padi.png", _png_bytes(300, 300)),
                "crop": "tidak-ada",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "invalid_request")

    @mock.patch(
        "analysis.views.requests.post",
        side_effect=requests.exceptions.ConnectionError,
    )
    def test_unreachable_ai_service_returns_503_not_fake_success(self, _mock_post):
        """AI service mati, jadi hasil harus 503 dan bukan diagnosis palsu."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self.client.post(
                self.url,
                {"image": _named_file("padi.png", _png_bytes(300, 300))},
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["error"]["code"], "service_unavailable")

    @mock.patch(
        "analysis.views.requests.post",
        side_effect=requests.exceptions.ConnectionError,
    )
    def test_failed_analysis_is_recorded_with_failed_status(self, _mock_post):
        """Percobaan yang gagal harus tercatat dengan status `failed`."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            self.client.post(
                self.url,
                {"image": _named_file("padi.png", _png_bytes(300, 300))},
                format="multipart",
            )

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.status, Analysis.Status.FAILED)
        self.assertTrue(analysis.message)


class AnalysisInferenceTests(APITestCase):
    """Perilaku backend terhadap berbagai respons AI service."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="petani", password="RahasiaKuat123"
        )
        self.client.force_authenticate(self.user)
        self.url = reverse("analysis-list")
        self.disease = Disease.objects.create(
            code="padi-blast",
            name="Blast",
            source="Test",
        )

    def _post_image(self):
        return self.client.post(
            self.url,
            {"image": _named_file("padi.png", _png_bytes(300, 300))},
            format="multipart",
        )

    @staticmethod
    def _response(status_code: int, payload: dict):
        response = mock.Mock()
        response.status_code = status_code
        response.headers = {"content-type": "application/json"}
        response.json.return_value = payload
        return response

    @mock.patch("analysis.views.requests.post")
    def test_model_unavailable_is_passed_through(self, mock_post):
        """Model yang belum tersedia harus dilaporkan sebagai model_unavailable."""
        mock_post.return_value = self._response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {
                "detail": {
                    "error": {
                        "code": "model_unavailable",
                        "message": "Model belum tersedia.",
                    }
                }
            },
        )

        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self._post_image()

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["error"]["code"], "model_unavailable")

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.status, Analysis.Status.FAILED)
        self.assertIsNone(analysis.predicted_disease)

    @mock.patch("analysis.views.requests.post")
    def test_valid_prediction_is_stored(self, mock_post):
        """Prediksi valid disimpan bersama penyakit dan confidence."""
        mock_post.return_value = self._response(
            status.HTTP_200_OK,
            {
                "status": "ok",
                "prediction": {
                    "class_id": "padi-blast",
                    "confidence": 0.91,
                    "model_version": "test-1",
                },
                "message": "Perkiraan awal.",
            },
        )

        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self._post_image()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.status, Analysis.Status.COMPLETED)
        self.assertEqual(analysis.predicted_disease, self.disease)
        self.assertAlmostEqual(analysis.confidence, 0.91)
        self.assertEqual(analysis.model_version, "test-1")

    @mock.patch("analysis.views.requests.post")
    def test_unknown_class_is_not_presented_as_result(self, mock_post):
        """Kelas yang tidak terdaftar tidak boleh menjadi hasil sukses."""
        mock_post.return_value = self._response(
            status.HTTP_200_OK,
            {
                "status": "ok",
                "prediction": {
                    "class_id": "tidak-terdaftar",
                    "confidence": 0.8,
                },
                "message": "",
            },
        )

        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self._post_image()

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["error"]["code"], "inference_failed")

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.status, Analysis.Status.FAILED)
        self.assertIsNone(analysis.predicted_disease)

    @mock.patch("analysis.views.requests.post")
    def test_invalid_confidence_is_not_presented_as_result(self, mock_post):
        """Confidence di luar 0..1 dianggap respons tidak valid."""
        mock_post.return_value = self._response(
            status.HTTP_200_OK,
            {
                "status": "ok",
                "prediction": {
                    "class_id": "padi-blast",
                    "confidence": 1.7,
                },
                "message": "",
            },
        )

        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            response = self._post_image()

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["error"]["code"], "inference_failed")
        self.assertEqual(Analysis.objects.get().status, Analysis.Status.FAILED)



class AnalysisImageAccessTests(APITestCase):
    """Gambar unggahan bersifat privat."""

    def setUp(self):
        self.user = User.objects.create_user(username="petani", password="RahasiaKuat123")
        self.other = User.objects.create_user(username="lain", password="RahasiaKuat123")

    def test_image_requires_authentication(self):
        """Tanpa login, gambar tidak bisa diakses."""
        analysis = Analysis.objects.create(
            user=self.user, status=Analysis.Status.COMPLETED
        )
        response = self.client.get(reverse("analysis-image", args=[analysis.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_cannot_access_image(self):
        """Pengguna lain tidak boleh melihat gambar milik orang ini."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            analysis = self._create_analysis_with_image()

            self.client.force_authenticate(self.other)
            response = self.client.get(reverse("analysis-image", args=[analysis.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_access_image(self):
        """Pemilik boleh membuka gambarnya sendiri."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            analysis = self._create_analysis_with_image()

            self.client.force_authenticate(self.user)
            response = self.client.get(reverse("analysis-image", args=[analysis.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("private", response["Cache-Control"])

    def test_serialized_image_url_is_private_endpoint(self):
        """URL gambar yang dikirim ke klien harus endpoint privat."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            analysis = self._create_analysis_with_image()

            self.client.force_authenticate(self.user)
            response = self.client.get(reverse("analysis-detail", args=[analysis.id]))

        self.assertEqual(
            response.data["image_url"],
            f"/api/v1/analyses/{analysis.id}/image/",
        )
        self.assertNotIn("/media/", response.data["image_url"])

    def _create_analysis_with_image(self) -> Analysis:
        """Buat record analisis dengan berkas gambar."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        analysis = Analysis.objects.create(
            user=self.user,
            status=Analysis.Status.COMPLETED,
        )
        analysis.image.save("gambar.png", _named_file("gambar.png", _png_bytes(50, 50)))
        return analysis


class AnalysisCropTests(APITestCase):
    """Pemilihan jenis tanaman."""

    def setUp(self):
        self.user = User.objects.create_user(username="petani", password="RahasiaKuat123")
        self.client.force_authenticate(self.user)
        self.crop = Crop.objects.create(code="padi", name="Padi")

    def test_active_crop_is_accepted(self):
        """Tanaman aktif boleh dikirim dan tersimpan pada record."""
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            self.client.post(
                reverse("analysis-list"),
                {
                    "image": _named_file("padi.png", _png_bytes(300, 300)),
                    "crop": "padi",
                },
                format="multipart",
            )

        analysis = Analysis.objects.get()
        self.assertEqual(analysis.crop, self.crop)


def _named_file(name: str, content: bytes):
    """Buat berkas unggahan sederhana untuk test."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(name, content, content_type="image/png")


def _png_bytes(width: int, height: int) -> bytes:
    """Hasilkan byte PNG berukuran tertentu."""
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(90, 150, 60)).save(buffer, format="PNG")
    return buffer.getvalue()
