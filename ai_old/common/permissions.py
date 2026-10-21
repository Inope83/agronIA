"""Permission khusus Agronia."""

from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Hanya pemilik objek yang boleh mengubah atau menghapus.

    Objek harus memiliki atribut `user`. Permintaan baca tetap boleh
    dilakukan bila objek memang publik (misalnya daftar tanaman).
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None)
        return owner is not None and owner == request.user
