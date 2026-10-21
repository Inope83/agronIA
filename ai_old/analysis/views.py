"""Endpoint analisis gambar.

Alur satu permintaan:

1. Validasi autentikasi dan izin.
2. Validasi berkas gambar (ukuran, format sebenarnya, keterbacaan).
3. Simpan record analisis dengan status `pending`.
4. Jalankan inferensi lewat `ai_service`.
5. Simpan hasil, atau simpan kegagalan beserta alasannya.

Aturan penting: kegagalan inferensi **tidak pernah** diubah menjadi hasil
sukses. Kalau model tidak tersedia, permintaan berakhir dengan status HTTP
503 dan kode error `model_unavailable` (lihat `docs/api.md` dan
`docs/ai-model.md`).
"""

from __future__ import annotations

import logging
import mimetypes

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_service.exceptions import (
    InferenceError,
    ModelUnavailable,
    UnsupportedClass,
    UnsupportedInput,
)
from ai_service.inference import InferenceService, load_image
from analysis.models import Analysis
from analysis.serializers import AnalysisCreateSerializer, AnalysisSerializer

logger = logging.getLogger(__name__)


class AnalysisViewSet(viewsets.ViewSet):
    """Buat dan daftar analisis milik pengguna yang sedang masuk."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Record hanya milik pemilik, tidak ada akses silang antar pengguna."""
        return Analysis.objects.filter(user=self.request.user).select_related(
            "crop", "predicted_disease"
        )

    def list(self, request):
        """Daftar riwayat analisis milik pengguna."""
        queryset = self.get_queryset()
        serializer = AnalysisSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Terima satu gambar dan jalankan analisis."""
        serializer = AnalysisCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        analysis = Analysis.objects.create(
            user=request.user,
            crop=serializer.validated_data.get("crop"),
            image=serializer.validated_data["image"],
            status=Analysis.Status.PROCESSING,
        )

        try:
            self._run_inference(analysis)
        except ModelUnavailable as exc:
            return self._fail(analysis, exc, status.HTTP_503_SERVICE_UNAVAILABLE)
        except UnsupportedInput as exc:
            return self._fail(analysis, exc, status.HTTP_400_BAD_REQUEST)
        except UnsupportedClass as exc:
            return self._fail(analysis, exc, status.HTTP_400_BAD_REQUEST)
        except InferenceError as exc:
            return self._fail(analysis, exc, status.HTTP_500_INTERNAL_SERVER_ERROR)

        analysis.refresh_from_db()
        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED,
        )

    def _run_inference(self, analysis: Analysis) -> None:
        """Jalankan model dan simpan hasilnya ke record analisis."""
        service = InferenceService()

        with analysis.image.open("rb") as image_file:
            image = load_image(image_file)

        prediction = service.predict(image)

        analysis.status = Analysis.Status.COMPLETED
        analysis.confidence = prediction.confidence
        analysis.model_version = prediction.model_version

        if prediction.is_confident:
            analysis.message = (
                "Hasil ini merupakan perkiraan awal. Periksa gejala pada tanaman "
                "dan konsultasikan dengan tenaga pertanian bila masalah berlanjut."
            )
        else:
            analysis.message = (
                "Keyakinan model terhadap hasil ini masih rendah, sehingga "
                "penyakit belum dapat dipastikan. Ambil foto lebih jelas dan "
                "coba lagi, atau konsultasikan dengan tenaga pertanian."
            )

        analysis.save(
            update_fields=[
                "status",
                "confidence",
                "model_version",
                "message",
                "updated_at",
            ]
        )

    def _fail(self, analysis: Analysis, exc: Exception, http_status: int) -> Response:
        """Catat kegagalan dan kembalikan error yang konsisten."""
        analysis.status = Analysis.Status.FAILED
        analysis.message = str(exc)
        analysis.save(update_fields=["status", "message", "updated_at"])

        logger.warning("Analisis %s gagal: %s", analysis.id, exc)

        error_code = getattr(exc, "default_code", None) or "inference_failed"
        if isinstance(exc, ModelUnavailable):
            error_code = "model_unavailable"
        elif isinstance(exc, UnsupportedInput):
            error_code = "unsupported_image"
        elif isinstance(exc, UnsupportedClass):
            error_code = "unsupported_class"

        return Response(
            {"error": {"code": error_code, "message": str(exc)}},
            status=http_status,
        )


class AnalysisDetailView(APIView):
    """Ambil satu analisis milik pengguna yang sedang masuk."""

    permission_classes = [IsAuthenticated]

    def get(self, request, analysis_id):
        """Tampilkan detail satu record analisis."""
        analysis = get_object_or_404(
            Analysis.objects.filter(user=request.user).select_related(
                "crop", "predicted_disease"
            ),
            pk=analysis_id,
        )
        return Response(AnalysisSerializer(analysis).data)


class AnalysisImageView(APIView):
    """Sajikan berkas gambar analisis hanya kepada pemiliknya.

    Berkas unggahan bersifat privat (lihat `docs/security.md` bagian "File
    Upload Security"). URL media biasa tidak dipakai karena dapat diakses
    siapa saja yang mengetahui tautannya.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, analysis_id):
        """Kirim berkas gambar bila pengguna adalah pemiliknya."""
        analysis = get_object_or_404(
            Analysis.objects.filter(user=request.user),
            pk=analysis_id,
        )

        if not analysis.image:
            raise NotFound("Berkas gambar tidak ditemukan.")

        try:
            handle = analysis.image.open("rb")
        except (FileNotFoundError, ValueError) as exc:
            raise NotFound("Berkas gambar tidak ditemukan.") from exc

        content_type, _ = mimetypes.guess_type(analysis.image.name)
        response = FileResponse(
            handle,
            content_type=content_type or "application/octet-stream",
        )
        # Gambar bersifat privat, jangan disimpan oleh cache bersama.
        response["Cache-Control"] = "private, no-store"
        response["Content-Disposition"] = 'inline; filename="analisis.jpg"'
        return response
