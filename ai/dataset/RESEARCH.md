# Agronia — Dataset Research (Phase 5)

**Tanggal:** 2026-10-22  
**Status:** In Progress  
**Branch:** backend-foundation  
**Tujuan:** Menentukan dataset + model awal yang aman, legal, dan relevan untuk Timor-Leste

## 1. Pertimbangan Awal - Tanaman di Timor-Leste

Berdasarkan konteks pertanian Timor-Leste (subtropis/tropis), tanaman yang umum dibudidayakan:
- Padi (Oryza sativa) - makanan pokok
- Jagung (Zea mays)
- Ubi kayu (Manihot esculenta)
- Kacang-kacangan
- Kopi (lebih komersial)
- Sayur-sayuran

Untuk **MVP pertama**, lebih bijak mulai dari **1-2 tanaman** dengan dataset publik yang berkualitas, lalu perluas bertahap.

## 2. Kandidat Dataset

### 2.1 PlantVillage (https://plantvillage.psu.edu/)
- **Sumber:** Penn State University
- **Ukuran:** ~54,000 gambar (versi asli)
- **Kelas:** Banyak kombinasi tanaman + penyakit
- **Kondisi:** Gambar diambil di laboratorium/controlled environment (bukan lapangan)
- **Lisensi:** Umumnya digunakan untuk riset akademik. Perlu cek lisensi terbaru di website resmi.
- **Kelebihan:** Bersih, terlabel dengan baik, cocok untuk baseline
- **Kekurangan:** Background seragam, tidak merepresentasikan kondisi lapangan Timor-Leste

### 2.2 PlantDoc (https://github.com/pratikkayal/PlantDoc-Dataset)
- **Sumber:** GitHub (research project)
- **Kondisi:** Lebih mendekati kondisi lapangan (in-the-wild)
- **Kelebihan:** Lebih realistis untuk deployment
- **Kekurangan:** Ukuran lebih kecil, labeling bisa kurang konsisten

### 2.3 PlantVillage Dataset di Kaggle
- **Sumber:** Berbagai mirror di Kaggle
- **Catatan:** Harus verifikasi lisensi per upload (bisa beda dari sumber asli)

## 3. Kriteria Seleksi (berdasarkan docs/dataset.md)

| Kriteria | Target | Status |
|---|---|---|
| Lisensi jelas & bisa dipakai untuk riset/prototipe | Wajib | Perlu verifikasi |
| Minimal 1 tanaman relevan untuk Timor-Leste | Wajib | Akan dicek |
| Label berkualitas | Wajib | Akan dicek |
| Cukup untuk baseline (minimal ratusan gambar per kelas) | Wajib | Akan dicek |
| Format gambar bisa diproses (JPG/PNG) | Wajib | Biasanya ok |
| Tidak ada issue copyright yang jelas | Wajib | Akan dicek |

## 4. Rekomendasi Awal

**Rekomendasi MVP:** Mulai dengan **Padi (Rice)** karena:
1. Makanan pokok di Timor-Leste
2. Ada dataset penyakit padi di PlantVillage/PlantDoc
3. Cukup penting untuk petani
4. Relatif mudah dapat baseline model

**Model kandidat:** 
- **MobileNetV2** - ringan, cocok untuk inference di server terbatas, cepat
- **EfficientNet-B0** - akurasi lebih baik, masih relatif ringan
- **ResNet50** - lebih berat tapi robust

Untuk MVP awal, **MobileNetV2 dengan pretrained ImageNet** via transfer learning adalah pilihan paling aman.

## 5. Action Items

- [ ] Verifikasi lisensi PlantVillage terbaru
- [ ] Cek ketersediaan kelas penyakit padi
- [ ] Evaluasi ukuran dataset per kelas
- [ ] Tentukan 2-4 kelas penyakit padi untuk MVP (jangan terlalu banyak)
- [ ] Download sample kecil untuk inspeksi (hanya jika lisensi aman)
- [ ] Dokumentasikan hasil di file ini

**Catatan:** Belum download dataset apapun. Semua keputusan harus berdasarkan dokumen resmi + inspeksi lisensi.
