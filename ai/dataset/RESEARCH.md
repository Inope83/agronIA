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
- **Kekurangan:** Background seragam, tidak merepresentasikan kondisi lapangan Timor-Leste, dan **tidak memiliki kelas padi**

### 2.2 PlantDoc (https://github.com/pratikkayal/PlantDoc-Dataset)
- **Sumber:** GitHub (research project)
- **Kondisi:** Lebih mendekati kondisi lapangan (in-the-wild)
- **Kelebihan:** Lebih realistis untuk deployment
- **Kekurangan:** Ukuran lebih kecil, labeling bisa kurang konsisten, dan **tidak memiliki kelas padi**

### 2.3 PlantVillage Dataset di Kaggle
- **Sumber:** Berbagai mirror di Kaggle
- **Catatan:** Harus verifikasi lisensi per upload (bisa beda dari sumber asli)

### 2.4 Rice Leaf and Crop Disease Detection (Labib dkk., 2024)
- **DOI:** [10.17632/g7tcwvshff.1](https://data.mendeley.com/datasets/g7tcwvshff/1)
- **Lisensi:** CC BY 4.0 (diverifikasi 2026-10-22)
- **Isi:** 2.508 gambar asli + 8.258 augmentasi; kelas Bacterial Leaf Blight, Rice Blast, Tungro, Healthy Leaf, dan Rice (generik)
- **Kelebihan:** Ada kelas *healthy*, jumlah memadai untuk baseline, kondisi foto lapangan
- **Kekurangan:** Kelas "Rice" ambigu; augmentasi bawaan tidak boleh dipakai untuk validasi/test

### 2.5 Rice Leaf Disease Image Samples (Sethy dkk., 2020/2024)
- **DOI:** [10.17632/fwcj7stb8r.2](https://data.mendeley.com/datasets/fwcj7stb8r/2)
- **Lisensi:** CC BY 4.0 (diverifikasi 2026-10-22)
- **Isi:** 5.932 gambar; Bacterial blight, Blast, Brown Spot, Tungro
- **Kelebihan:** Jumlah besar, empat penyakit penting
- **Kekurangan:** Tidak ada kelas *healthy*, sehingga tidak bisa membedakan daun sehat

### 2.6 Rice Leaf Bacterial and Fungal Disease (Hasan dkk., 2023)
- **DOI:** [10.17632/hx6f852hw4.2](https://data.mendeley.com/datasets/hx6f852hw4/2)
- **Lisensi:** CC BY 4.0 (diverifikasi 2026-10-22)
- **Isi:** 1.701 gambar asli + 5.188 augmentasi; 8 kelas termasuk Healthy
- **Kelebihan:** Kondisi lapangan Bangladesh, ada *healthy*, split bawaan
- **Kekurangan:** Delapan kelas terlalu banyak untuk MVP pertama

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
2. Tersedia dataset padi spesifik dengan lisensi CC BY 4.0 (lihat 2.4–2.6)
3. Cukup penting untuk petani
4. Relatif mudah mendapat baseline model

**Kandidat utama:** dataset 2.4 dengan 4 kelas (Bacterial Leaf Blight, Rice Blast, Tungro, Healthy Leaf). Hanya gambar asli yang dipakai; keputusan final setelah inspeksi dataset.

**Model kandidat:** 
- **MobileNetV2** - ringan, cocok untuk inference di server terbatas, cepat
- **EfficientNet-B0** - akurasi lebih baik, masih relatif ringan
- **ResNet50** - lebih berat tapi robust

Untuk MVP awal, **MobileNetV2 dengan pretrained ImageNet** via transfer learning adalah pilihan paling aman.

## 5. Action Items

- [x] Verifikasi lisensi kandidat dataset padi (CC BY 4.0, 2026-10-22)
- [x] Pastikan kandidat memiliki kelas padi (PlantVillage/PlantDoc tidak punya)
- [ ] Unduh kandidat utama dan inspeksi struktur folder
- [ ] Evaluasi ukuran dataset asli per kelas
- [x] Tentukan 4 kelas MVP: Bacterial Leaf Blight, Rice Blast, Tungro, Healthy Leaf
- [ ] Download sample kecil untuk inspeksi visual
- [ ] Dokumentasikan hasil inspeksi di file ini

**Catatan:** Belum download dataset apapun. Semua keputusan harus berdasarkan dokumen resmi + inspeksi lisensi.
