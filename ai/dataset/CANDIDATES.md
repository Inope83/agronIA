# Kandidat Dataset untuk Agronia (MVP)

**Status:** In Progress  
**Tujuan:** Cari dataset yang bisa dipakai buat baseline klasifikasi penyakit tanaman

## 1. Perbandingan Kandidat

### 1.1 Dataset padi (lisensi sudah diverifikasi)

| Dataset | Sumber | Kelas | Ukuran | Lisensi | Status |
|---|---|---|---|---|---|
| **Rice Leaf and Crop Disease Detection** | [DOI 10.17632/g7tcwvshff.1](https://data.mendeley.com/datasets/g7tcwvshff/1) | Bacterial Leaf Blight, Rice Blast, Tungro, Healthy Leaf, Rice (generik) | 2.508 asli + 8.258 augmentasi | CC BY 4.0 | **Kandidat utama** |
| **Rice Leaf Disease Image Samples** | [DOI 10.17632/fwcj7stb8r.2](https://data.mendeley.com/datasets/fwcj7stb8r/2) | Bacterial blight, Blast, Brown Spot, Tungro | 5.932 | CC BY 4.0 | Cadangan (tanpa *healthy*) |
| **Rice Leaf Bacterial and Fungal Disease** | [DOI 10.17632/hx6f852hw4.2](https://data.mendeley.com/datasets/hx6f852hw4/2) | 8 kelas termasuk Healthy | 1.701 asli + 5.188 augmentasi | CC BY 4.0 | Cadangan (kelas lebih banyak) |
| **UCI Rice Leaf Diseases** | [UCI 486](https://archive.ics.uci.edu/dataset/486/rice+leaf+diseases) | Bacterial leaf blight, Brown spot, Leaf smut | 120 | CC BY 4.0 | Terlalu kecil untuk training utama |

### 1.2 Dataset non-padi (referensi, bukan untuk MVP)

| Dataset | Catatan | Status |
|---|---|---|
| **PlantVillage** | ~54k gambar, kualitas label bagus, tetapi **tidak memiliki kelas padi** dan kondisi lab | Tidak dipakai untuk MVP padi |
| **PlantDoc** | 2.598 gambar in-the-wild, tetapi **tidak memiliki kelas padi** | Tidak dipakai untuk MVP padi |
| **Plant Pathology (FGVC)** | Fokus apel, bukan padi | Tidak relevan untuk MVP |

## 2. Rekomendasi Untuk MVP

Berdasarkan kebutuhan Agronia (fokus ke petani Timor-Leste), urutannya gini:

| Prioritas | Tanaman | Alasan |
|---|---|---|
| **#1** | **Padi (Oryza sativa)** | Makanan pokok di Timor-Leste, peluang dampak paling besar buat petani |
| **#2** | **Jagung (Zea mays)** | Cukup umum dibudidayakan, ada potensi dataset |
| **#3** | **Ubi Kayu (Manihot esculenta)** | Sangat umum, tapi dataset penyakitnya biasanya lebih terbatas |

**Rekomendasi:** Mulai dari **Padi saja** buat MVP pertama. Jangan langsung ambil 5-10 tanaman. Lebih baik **sedikit kelas, tapi bisa diuji dengan jujur** ketimbang banyak kelas tapi nggak relevan.

**Kandidat utama:** **Rice Leaf and Crop Disease Detection** (Labib dkk., 2024, CC BY 4.0) dengan 4 kelas MVP:

1. Bacterial Leaf Blight
2. Rice Blast
3. Tungro
4. Healthy Leaf

Kelas **"Rice"** (generik) tidak dipakai karena bukan diagnosis penyakit. Hanya gambar **asli/raw** yang dipakai untuk training/validasi/test; gambar augmentasi bawaan tidak dipakai agar tidak terjadi kebocoran data. Keputusan final menunggu inspeksi dataset setelah diunduh (jumlah per kelas, duplikat, kualitas label, dan kondisi foto).

## 3. Rekomendasi Model

| Model | Bobot | Cocok Inference | Catatan |
|---|---|---|---|
| **MobileNetV2** | Ringan (~14MB) | Sangat cocok (CPU/server ringan) | Paling aman buat MVP. Transfer learning dari ImageNet. Cukup kuat buat baseline. |
| **EfficientNet-B0** | Sedang (~20MB) | Cocok | Akurasi biasanya lebih baik, masih bisa jalan di CPU. |
| **ResNet50** | Lebih berat (~98MB) | Kurang ideal awal | Akurasi bagus, tapi overkill buat mulai. Bisa dipertimbangkan nanti kalo perlu. |

**Rekomendasi awal:** **MobileNetV2 + ImageNet pretrained**. Ringan, gampang diintegrasi ke `ai/service/`, dan nggak makan resource berlebihan.

## 4. Langkah Selanjutnya

- [x] **Verifikasi lisensi** - Tiga dataset padi di 1.1 sudah CC BY 4.0 (dicek di halaman Mendeley, 2026-10-22).
- [x] **Pastikan ada kelas padi** - PlantVillage/PlantDoc tidak punya padi; gunakan dataset padi spesifik di 1.1.
- [ ] **Unduh kandidat utama** - Simpan ke `ai/dataset/raw/`, lalu inspeksi isi dan struktur folder.
- [ ] **Mapping kelas** - Cocokkan nama kelas dataset dengan `Disease.code` di backend.
- [ ] **Cek distribusi** - Hitung gambar asli per kelas; jangan gabungkan augmentasi ke train/val/test.
- [ ] **Siapkan split** - Train/val/test (mis. 70/15/15) stratified, dibuat sekali dan disimpan sebagai daftar file.
- [ ] **Evaluasi realistis** - Catat asal dataset dan keterbatasannya di `docs/ai-model.md`.

## Catatan Penting

- **Belum ada dataset yang diunduh.** Lisensi sudah diverifikasi, isi dataset belum.
- **Jangan klaim akurasi** sebelum ada evaluasi terpisah di test set + dokumentasi metrik per kelas.
- **Fokus ke bukti.** Lisensi jelas dan jumlah gambar per kelas lebih penting daripada popularitas dataset.
- **Kondisi lapangan beda.** Foto dataset belum tentu mirip foto petani Timor-Leste; ini harus diuji dan dicatat sebagai keterbatasan.