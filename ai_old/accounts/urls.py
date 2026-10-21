"""Rute API untuk autentikasi dan profil.

Rute ini di-`include` pada `api/v1/auth/`, jadi path di bawah ini relatif
terhadap prefix tersebut.
"""

from __future__ import annotations

from django.urls import path

from accounts.views import LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
]
