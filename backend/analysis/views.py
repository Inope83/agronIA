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

import requests
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
        except Exception as exc:
            return self._fail(analysis, exc, status.HTTP_503_SERVICE_UNAVAILABLE)

        analysis.refresh_from_db()
        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED,
        )

    def _run_inference(self, analysis: Analysis) -> None:
        """Kirim gambar ke AI service terpisah dan simpan hasilnya."""
        ai_url = getattr(settings, "AI_SERVICE_URL", "http://localhost:8001")
        timeout = getattr(settings, "AI_SERVICE_TIMEOUT", 30)

        try:
            with analysis.image.open("rb") as image_file:
                files = {"file": (analysis.image.name, image_file.read(), "image/jpeg")}
            resp = requests.post(f"{ai_url}/predict", files=files, timeout=timeout)
        except requests.exceptions.ConnectionError as exc:
            raise Exception(
                "AI service tidak dapat dijangkau. Pastikan service AI berjalan di "
                f"{ai_url}."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise Exception("Permintaan ke AI service melebihi batas waktu.") from exc

        if resp.status_code == 503:
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            err = data.get("error") or {}
            raise Exception(err.get("message") or "Layanan analisis AI tidak tersedia.")

        if resp.status_code != 200:
            raise Exception("AI service mengembalikan respons yang tidak valid.")

        try:
            result = resp.json()
        except ValueError as exc:
            raise Exception("Respons AI service bukan JSON yang valid.") from exc

        prediction = result.get("prediction") or {}

        analysis.status = Analysis.Status.COMPLETED
        analysis.confidence = prediction.get("confidence")
        analysis.model_version = prediction.get("model_version") or ""
        analysis.message = result.get("message") or (
            "Hasil ini merupakan perkiraan awal. Periksa gejala pada tanaman "
            "dan konsultasikan dengan tenaga pertanian bila masalah berlanjut."
        )

        # Jika AI service mengembalikan class_id, kita simpan sebagai info di message
        # Karena model mapping butuh research lebih lanjut
        class_id = prediction.get("class_id")
        if class_id:
            analysis.message = f"[{class_id}] {analysis.message}"

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

        error_code = "service_unavailable"
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
