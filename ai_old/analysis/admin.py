"""Pendaftaran model analisis di Django Admin."""

from __future__ import annotations

from django.contrib import admin

from analysis.models import Analysis


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "crop", "status", "confidence", "created_at")
    list_filter = ("status", "crop")
    search_fields = ("user__username", "message")
    readonly_fields = ("id", "created_at", "updated_at")
    # Berkas unggahan tidak boleh dihapus lewat panel admin.
    exclude = ("image",)
