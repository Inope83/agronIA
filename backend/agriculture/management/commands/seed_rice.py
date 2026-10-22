"""Seed tanaman padi dan kelas model AI MVP."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from agriculture.models import Crop, Disease

CROP_CODE = "padi"

DISEASES = [
    {
        "code": "padi-bacterial-blight",
        "name": "Bacterial Leaf Blight",
        "name_local": "Hawar Daun Bakteri",
        "symptoms": (
            "Bercak panjang berair pada daun yang berubah menjadi kuning "
            "hingga putih. Serangan berat dapat membuat daun mengering, "
            "menggulung, dan tanaman tampak layu."
        ),
        "prevention": (
            "Gunakan varietas tahan dan benih bersertifikat, hindari pupuk "
            "nitrogen berlebihan, jaga drainase, serta bersihkan sisa tanaman."
        ),
        "management": (
            "Buang bagian tanaman yang terinfeksi, hindari memindahkan air "
            "dari petak terserang, dan konsultasikan langkah pengendalian "
            "dengan penyuluh pertanian setempat."
        ),
        "source": (
            "IRRI Rice Knowledge Bank - Bacterial Blight. "
            "International Rice Research Institute."
        ),
    },
    {
        "code": "padi-sehat",
        "name": "Healthy Rice Leaf",
        "name_local": "Daun Padi Sehat",
        "symptoms": (
            "Daun berwarna hijau merata tanpa bercak, lesi, atau perubahan "
            "bentuk yang mencolok."
        ),
        "prevention": (
            "Pertahankan pemupukan berimbang, irigasi yang baik, rotasi "
            "tanaman, dan pengamatan rutin di lahan."
        ),
        "management": (
            "Lanjutkan perawatan dan pantau tanaman secara berkala. Ambil "
            "foto ulang bila muncul gejala baru."
        ),
        "source": (
            "Kriteria kelas Healthy Leaf pada dataset Labib et al. (2024), "
            "DOI 10.17632/g7tcwvshff.1; praktik budidaya umum IRRI Rice "
            "Knowledge Bank."
        ),
    },
    {
        "code": "padi-blast",
        "name": "Rice Blast",
        "name_local": "Blas",
        "symptoms": (
            "Bercak berbentuk belah ketupat dengan pusat abu-abu dan tepi "
            "cokelat pada daun. Serangan juga dapat mengenai leher malai "
            "dan menyebabkan bulir hampa."
        ),
        "prevention": (
            "Gunakan varietas tahan dan benih sehat, hindari nitrogen "
            "berlebihan, atur waktu tanam, serta jaga kelembapan lahan."
        ),
        "management": (
            "Bersihkan sisa tanaman terinfeksi, terapkan rotasi tanaman, "
            "dan konsultasikan penggunaan fungisida dengan penyuluh."
        ),
        "source": (
            "IRRI Rice Knowledge Bank - Rice Blast. "
            "International Rice Research Institute."
        ),
    },
    {
        "code": "padi-tungro",
        "name": "Tungro",
        "name_local": "Tungro",
        "symptoms": (
            "Daun menguning hingga oranye mulai dari ujung, tanaman kerdil, "
            "dan jumlah anakan berkurang. Penyakit ini disebabkan virus yang "
            "ditularkan oleh wereng hijau."
        ),
        "prevention": (
            "Gunakan varietas tahan, tanam serempak, kendalikan wereng "
            "hijau, serta bersihkan gulma dan sisa tanaman."
        ),
        "management": (
            "Cabut tanaman bergejala berat, pantau populasi wereng, dan "
            "koordinasikan pengendalian dengan petani di sekitar lahan."
        ),
        "source": (
            "IRRI Rice Knowledge Bank - Tungro. "
            "International Rice Research Institute."
        ),
    },
]


class Command(BaseCommand):
    help = "Membuat data tanaman padi dan empat kelas penyakit untuk model AI MVP."

    @transaction.atomic
    def handle(self, *args, **options):
        crop, crop_created = Crop.objects.update_or_create(
            code=CROP_CODE,
            defaults={
                "name": "Rice",
                "name_local": "Padi",
                "description": (
                    "Tanaman pangan utama di Timor-Leste. Model MVP mengenali "
                    "hawar daun bakteri, daun sehat, blas, dan tungro pada "
                    "daun padi."
                ),
                "is_active": True,
            },
        )

        created = 0
        updated = 0
        for item in DISEASES:
            disease, was_created = Disease.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "name_local": item["name_local"],
                    "symptoms": item["symptoms"],
                    "prevention": item["prevention"],
                    "management": item["management"],
                    "source": item["source"],
                    "is_active": True,
                },
            )
            disease.crops.add(crop)
            if was_created:
                created += 1
            else:
                updated += 1

        crop_state = "dibuat" if crop_created else "diperbarui"
        self.stdout.write(
            self.style.SUCCESS(
                f"Data padi siap: tanaman {crop_state}; "
                f"{created} penyakit baru, {updated} diperbarui."
            )
        )
