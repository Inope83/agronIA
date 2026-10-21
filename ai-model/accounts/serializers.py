"""Serializer untuk registrasi dan profil pengguna."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Data profil milik pengguna sendiri."""

    class Meta:
        model = Profile
        fields = ["role", "display_name", "created_at"]
        read_only_fields = ["created_at"]


class UserSerializer(serializers.ModelSerializer):
    """Representasi pengguna yang dikirim ke klien."""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    """Pendaftaran akun baru.

    Password divalidasi oleh validator bawaan Django, sehingga aturan
    kekuatannya sama dengan yang dipakai `createsuperuser`.
    """

    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    display_name = serializers.CharField(
        required=False, allow_blank=True, max_length=120
    )
    role = serializers.ChoiceField(
        choices=Profile.Role.choices, required=False, default=Profile.Role.FARMER
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "display_name",
            "role",
        ]

    def validate_email(self, value: str) -> str:
        """Email wajib diisi dan unik."""
        if not value:
            raise serializers.ValidationError("Email wajib diisi.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email sudah digunakan.")
        return value

    def validate_username(self, value: str) -> str:
        """Username harus unik dan tidak mengandung spasi."""
        if " " in value:
            raise serializers.ValidationError("Username tidak boleh mengandung spasi.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username sudah digunakan.")
        return value

    def validate(self, attrs):
        """Cocokkan password dan jalankan validator kekuatan password."""
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Konfirmasi password tidak cocok."}
            )

        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        """Buat user beserta profilnya."""
        display_name = validated_data.pop("display_name", "")
        role = validated_data.pop("role", Profile.Role.FARMER)

        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, role=role, display_name=display_name)
        return user
