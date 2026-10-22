"""Rute API untuk analisis gambar."""

from __future__ import annotations

from django.urls import path

from analysis.views import (
    AnalysisDetailView,
    AnalysisFeedbackView,
    AnalysisImageView,
    AnalysisViewSet,
)

urlpatterns = [
    path(
        "analyses/",
        AnalysisViewSet.as_view({"get": "list", "post": "create"}),
        name="analysis-list",
    ),
    path(
        "analyses/<uuid:analysis_id>/",
        AnalysisDetailView.as_view(),
        name="analysis-detail",
    ),
    path(
        "analyses/<uuid:analysis_id>/feedback/",
        AnalysisFeedbackView.as_view(),
        name="analysis-feedback",
    ),
    path(
        "analyses/<uuid:analysis_id>/image/",
        AnalysisImageView.as_view(),
        name="analysis-image",
    ),
]
