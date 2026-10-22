"""Endpoint analisis gambar.

Alur satu permintaan:

1. Validasi autentikasi dan izin.
2. Validasi berkas gambar (ukuran, format sebenarnya, keterbacaan).
3. Simpan record analisis dengan status `pending`.
4. Kirim gambar ke AI service terpisah via HTTP.
5. Simpan hasil, atau simpan kegagalan beserta alasannya.

Kegagalan AI service **tidak pernah** diubah menjadi hasil sukses.
"""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agriculture.models import Disease
from analysis.models import Analysis, AnalysisFeedback
from analysis.serializers import (
    AnalysisCreateSerializer,
    AnalysisFeedbackSerializer,
    AnalysisSerializer,
)

logger = logging.getLogger(__name__)


class InferenceError(Exception):
    """Kegagalan inferensi dengan kode error dan status HTTP yang jelas."""

    code = "inference_failed"
    http_status = status.HTTP_502_BAD_GATEWAY


class AiServiceUnavailable(InferenceError):
    """Layanan AI tidak dapat dijangkau atau tidak merespons."""

    code = "service_unavailable"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE


class AiModelUnavailable(InferenceError):
    """Layanan AI berjalan tetapi model belum tersedia."""

    code = "model_unavailable"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE


class InternalProcessingError(InferenceError):
    """Kesalahan tak terduga di sisi backend."""

    code = "internal_server_error"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR


def _extract_service_error(payload: Any) -> tuple[str | None, str | None]:
    """Ambil kode dan pesan error dari respons AI service."""
    if not isinstance(payload, dict):
        return None, None

    error = payload.get("error")
    if error is None:
        detail = payload.get("detail")
        if isinstance(detail, dict):
            error = detail.get("error", detail)
    if not isinstance(error, dict):
        return None, None

    code = error.get("code")
    message = error.get("message")
    return (
        code if isinstance(code, str) else None,
        message if isinstance(message, str) else None,
    )


class AnalysisViewSet(viewsets.ViewSet):
    """Buat dan daftar analisis milik pengguna yang sedang masuk."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Record hanya milik pemilik, tidak ada akses silang antar pengguna."""
        return Analysis.objects.filter(user=self.request.user).select_related(
            "crop", "predicted_disease", "feedback__suggested_disease"
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
        except InferenceError as exc:
            return self._fail(analysis, exc)
        except Exception:
            logger.exception("Kesalahan tak terduga saat menganalisis %s", analysis.id)
            return self._fail(
                analysis,
                InternalProcessingError(
                    "Terjadi kesalahan internal saat memproses analisis."
                ),
            )

        analysis.refresh_from_db()
        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED,
        )

    def _run_inference(self, analysis: Analysis) -> None:
        """Kirim gambar ke AI service terpisah dan simpan hasilnya."""
        ai_url = getattr(settings, "AI_SERVICE_URL", "http://localhost:8001")
        timeout = getattr(settings, "AI_SERVICE_TIMEOUT", 30)

        content_type, _ = mimetypes.guess_type(analysis.image.name)
        content_type = content_type or "application/octet-stream"

        try:
            with analysis.image.open("rb") as image_file:
                files = {
                    "file": (
                        Path(analysis.image.name).name,
                        image_file,
                        content_type,
                    )
                }
                response = requests.post(
                    f"{ai_url}/predict",
                    files=files,
                    timeout=timeout,
                )
        except requests.exceptions.ConnectionError as exc:
            raise AiServiceUnavailable(
                "Layanan analisis AI tidak dapat dijangkau. Silakan coba lagi nanti."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise AiServiceUnavailable(
                "Layanan analisis AI tidak merespons tepat waktu. Silakan coba lagi."
            ) from exc

        if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            code, message = _extract_service_error(self._safe_json(response))
            if code == "model_unavailable":
                raise AiModelUnavailable(
                    message or "Model AI belum tersedia untuk melakukan analisis."
                )
            raise AiServiceUnavailable(
                message or "Layanan analisis AI sedang tidak tersedia."
            )

        if response.status_code != status.HTTP_200_OK:
            logger.warning(
                "AI service mengembalikan status %s untuk analisis %s",
                response.status_code,
                analysis.id,
            )
            raise InferenceError(
                "Layanan analisis AI mengembalikan respons yang tidak valid."
            )

        result = self._safe_json(response)
        if not isinstance(result, dict):
            raise InferenceError("Respons layanan AI bukan JSON yang valid.")

        prediction = result.get("prediction")
        if not isinstance(prediction, dict):
            raise InferenceError("Layanan AI tidak mengembalikan prediksi.")

        class_id = prediction.get("class_id")
        if not isinstance(class_id, str) or not class_id:
            raise InferenceError("Layanan AI tidak mengembalikan kelas prediksi.")

        disease = Disease.objects.filter(code=class_id, is_active=True).first()
        if disease is None:
            logger.warning(
                "Kelas '%s' dari AI service belum terdaftar untuk analisis %s",
                class_id,
                analysis.id,
            )
            raise InferenceError(
                "Model menghasilkan kelas yang belum terdaftar di sistem."
            )

        confidence = prediction.get("confidence")
        if confidence is not None:
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not 0.0 <= float(confidence) <= 1.0
            ):
                raise InferenceError(
                    "Nilai confidence dari layanan AI tidak valid."
                )
            confidence = float(confidence)

        analysis.status = Analysis.Status.COMPLETED
        analysis.predicted_disease = disease
        analysis.confidence = confidence
        analysis.model_version = str(prediction.get("model_version") or "")[:100]
        analysis.message = result.get("message") or (
            "Hasil ini merupakan perkiraan awal. Periksa gejala pada tanaman "
            "dan konsultasikan dengan tenaga pertanian bila masalah berlanjut."
        )
        analysis.save(
            update_fields=[
                "status",
                "predicted_disease",
                "confidence",
                "model_version",
                "message",
                "updated_at",
            ]
        )

    @staticmethod
    def _safe_json(response: requests.Response) -> Any:
        """Baca JSON tanpa melempar error bila isinya bukan JSON."""
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return None
        try:
            return response.json()
        except ValueError:
            return None

    def _fail(self, analysis: Analysis, exc: InferenceError) -> Response:
        """Catat kegagalan dan kembalikan error yang konsisten."""
        analysis.status = Analysis.Status.FAILED
        analysis.message = str(exc)
        analysis.save(update_fields=["status", "message", "updated_at"])

        logger.warning("Analisis %s gagal (%s): %s", analysis.id, exc.code, exc)

        return Response(
            {"error": {"code": exc.code, "message": str(exc)}},
            status=exc.http_status,
        )


class AnalysisFeedbackView(APIView):
    """Simpan atau perbarui umpan balik pemilik analisis.

    Umpan balik tidak mengubah hasil analisis asli. Pengguna dapat
    memperbarui laporannya bila salah memilih.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, analysis_id):
        """Catat koreksi pengguna untuk analisis yang berhasil."""
        analysis = get_object_or_404(
            Analysis.objects.filter(user=request.user),
            pk=analysis_id,
        )
        if analysis.status != Analysis.Status.COMPLETED:
            return Response(
                {
                    "error": {
                        "code": "invalid_state",
                        "message": (
                            "Umpan balik hanya dapat dikirim untuk analisis "
                            "yang berhasil."
                        ),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalysisFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feedback, created = AnalysisFeedback.objects.update_or_create(
            analysis=analysis,
            defaults={
                "is_correct": serializer.validated_data["is_correct"],
                "suggested_disease": serializer.validated_data.get(
                    "suggested_disease"
                ),
                "note": serializer.validated_data.get("note", ""),
            },
        )

        return Response(
            AnalysisFeedbackSerializer(feedback).data,
            status=(
                status.HTTP_201_CREATED if created else status.HTTP_200_OK
            ),
        )


class AnalysisDetailView(APIView):
    """Ambil satu analisis milik pengguna yang sedang masuk."""

    permission_classes = [IsAuthenticated]

    def get(self, request, analysis_id):
        """Tampilkan detail satu record analisis."""
        analysis = get_object_or_404(
            Analysis.objects.filter(user=request.user).select_related(
                "crop", "predicted_disease", "feedback__suggested_disease"
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
