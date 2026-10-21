"""Pendaftaran model pertanian di Django Admin."""

from __future__ import annotations

from django.contrib import admin

from agriculture.models import AgriculturalResource, Crop, Disease


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "name_local", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "name_local")


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    filter_horizontal = ("crops",)


@admin.register(AgriculturalResource)
class AgriculturalResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_sample", "created_at")
    list_filter = ("category", "is_sample")
    search_fields = ("title", "summary")
