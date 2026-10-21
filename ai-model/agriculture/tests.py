"""Test untuk endpoint data pertanian."""

from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from agriculture.models import AgriculturalResource, Crop, Disease


class CropApiTests(APITestCase):
    """Endpoint daftar tanaman."""

    def setUp(self):
        self.crop = Crop.objects.create(code="padi", name="Padi", name_local="Rai")
        self.inactive = Crop.objects.create(code="x", name="X", is_active=False)

    def test_list_returns_active_crops(self):
        """Hanya tanaman aktif yang dikembalikan."""
        response = self.client.get(reverse("crop-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [item["code"] for item in response.data]
        self.assertIn("padi", codes)
        self.assertNotIn("x", codes)

    def test_list_does_not_require_authentication(self):
        """Daftar tanaman bisa diakses tanpa login."""
        response = self.client.get(reverse("crop-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_by_code(self):
        """Tanaman bisa diambil memakai kodenya."""
        response = self.client.get(reverse("crop-detail", args=[self.crop.code]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "padi")


class DiseaseApiTests(APITestCase):
    """Endpoint daftar penyakit."""

    def setUp(self):
        self.crop = Crop.objects.create(code="padi", name="Padi")
        self.disease = Disease.objects.create(
            code="blast-padi",
            name="Blast Padi",
            symptoms="Bercak berbentuk belah ketupat.",
            management="Gunakan varieties tahan dan ewab.",
            source="Balai Seedshift",
        )
        self.disease.crops.add(self.crop)

    def test_list_returns_diseases_with_crop_codes(self):
        """Daftar penyakit memuat kode tanaman yang terkait."""
        response = self.client.get(reverse("disease-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["crop_codes"], ["padi"])

    def test_disease_source_is_exposed(self):
        """Sumber informasi ikut dikirim supaya pengguna bisa memverifikasi."""
        response = self.client.get(reverse("disease-detail", args=[self.disease.code]))
        self.assertEqual(response.data["source"], "Balai Seedshift")


class AgriculturalResourceApiTests(APITestCase):
    """Endpoint materi belajar."""

    def test_list_is_paginated_and_marks_sample_content(self):
        """Materi contoh harus ditandai dengan `is_sample`."""
        AgriculturalResource.objects.create(
            title="Menanam Padi",
            summary="Panduan singkat.",
            is_sample=True,
        )

        response = self.client.get(reverse("resource-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["is_sample"])
