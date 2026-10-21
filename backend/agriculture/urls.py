"""Rute API untuk data pertanian."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from agriculture.views import AgriculturalResourceViewSet, CropViewSet, DiseaseViewSet

router = DefaultRouter()
router.register("crops", CropViewSet, basename="crop")
router.register("diseases", DiseaseViewSet, basename="disease")
router.register("resources", AgriculturalResourceViewSet, basename="resource")

urlpatterns = router.urls
