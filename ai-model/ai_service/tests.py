"""Test untuk lapisan inferensi AI.

Fokus test: memastikan sistem **tidak pernah** mengembalikan tebakan
ketika model belum tersedia (lihat `docs/ai-model.md` bagian "Uncertainty
Handling" dan MASTER_PROMPT Rule D).
"""

from __future__ import annotations

from io import BytesIO

from django.test import TestCase, override_settings
from PIL import Image

from ai_service.exceptions import ModelUnavailable
from ai_service.inference import InferenceService, load_image
from ai_service.registry import ClassRegistry


def make_image(width: int = 300, height: int = 300) -> Image.Image:
    """Buat gambar RGB sederhana untuk keperluan test."""
    return Image.new("RGB", (width, height), color=(120, 180, 90))


class ClassRegistryTests(TestCase):
    def test_registry_shipped_is_empty_so_no_class_is_claimed(self):
        """Daftar kelas bawaan harus kosong sampai model benar-benar dipilih."""
        registry = ClassRegistry.load()
        self.assertTrue(registry.is_empty)
        self.assertEqual(registry.model_version, "none")

    def test_load_missing_file_returns_empty_registry(self):
        """Berkas yang tidak ada tidak boleh menyebabkan crash."""
        registry = ClassRegistry.load(path=self._nonexistent_path())
        self.assertTrue(registry.is_empty)

    def test_contains_reports_membership(self):
        """Cek keanggotaan kelas berdasarkan id."""
        registry = ClassRegistry(model_version="v1", classes=("a", "b"))
        self.assertTrue(registry.contains("a"))
        self.assertFalse(registry.contains("z"))

    def _nonexistent_path(self):
        from pathlib import Path

        return Path("/tmp/agronia-tidak-ada-9999/classes.json")


class InferenceServiceTests(TestCase):
    def test_predict_raises_model_unavailable_without_model_path(self):
        """Tanpa model, inferensi harus gagal dengan jelas, bukan menebak."""
        service = InferenceService(model_path="")
        with self.assertRaises(ModelUnavailable):
            service.predict(make_image())

    def test_predict_raises_model_unavailable_when_file_missing(self):
        """Berkas model yang hilang harus menghasilkan error terkontrol."""
        service = InferenceService(model_path="/tmp/agronia-model-tidak-ada.pt")
        with self.assertRaises(ModelUnavailable):
            service.predict(make_image())

    def test_is_available_is_false_without_model(self):
        """Status ketersediaan harus_false tanpa model dan daftar kelas."""
        service = InferenceService(model_path="")
        self.assertFalse(service.is_available)

    def test_preprocess_resizes_to_model_input_size(self):
        """Ukuran input harus sesuai kontrak model."""
        service = InferenceService()
        with override_settings(AI_IMAGE_SIZE=224):
            prepared = service.preprocess(make_image(640, 480))
        self.assertEqual(prepared.size, (224, 224))

    def test_preprocess_converts_to_rgb(self):
        """Gambar non-RGB harus dikonversi ke RGB."""
        service = InferenceService()
        prepared = service.preprocess(make_image().convert("L"))
        self.assertEqual(prepared.mode, "RGB")

    def test_load_image_reads_valid_png(self):
        """PNG yang valid harus bisa dibaca."""
        buffer = BytesIO()
        make_image(100, 100).save(buffer, format="PNG")
        buffer.seek(0)

        image = load_image(buffer)
        self.assertEqual(image.size, (100, 100))

    def test_load_image_rejects_non_image(self):
        """Berkas teks harus ditolak sebagai gambar."""
        from ai_service.exceptions import UnsupportedInput

        buffer = BytesIO(b"ini bukan gambar")
        buffer.seek(0)

        with self.assertRaises(UnsupportedInput):
            load_image(buffer)
