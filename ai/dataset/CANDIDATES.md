# Kandidat Dataset untuk Agronia (MVP)

**Status:** In Progress  
**Tujuan:** Cari dataset yang bisa dipakai buat baseline klasifikasi penyakit tanaman

## 1. Perbandingan Kandidat

| Dataset | Sumber | Kondisi Gambar | Ukuran | Kelebihan | Kekurangan | Lisensi | Status |
|---|---|---|---|---|---|---|---|
| **PlantVillage** | [plantvillage.psu.edu](https://plantvillage.psu.edu/) | Lab / controlled (daun terlepas, background seragam) | ~54k gambar, banyak kelas tanaman & penyakit | Sangat bersih, label konsisten, cocok buat *baseline*, banyak dipakai riset | Kurang mirip kondisi lapangan Timor-Leste, background terlalu ideal | Perlu dicek langsung di Terms of Service | **Perlu verifikasi** |
| **PlantDoc** | [github.com/pratikkayal/PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset) | In-the-wild / lapangan (background alami, pencahayaan beragam) | ~2.6k gambar | Lebih realistis buat deployment ke petani, mendekati foto asli dari handphone | Lebih kecil, distribusi kelas nggak selalu seimbang, ada label yang perlu dicek ulang | Perlu cek LICENSE di repo GitHub | **Perlu verifikasi** |
| **Rice Disease Dataset (Kaggle mirrors)** | [kaggle.com/search?q=rice+disease](https://www.kaggle.com/search?q=rice+disease) | Campuran (ada yang lab, ada yang lapangan) | Beragam (ratusan - ribuan) | Lebih fokus ke **padi** (sangat relevan buat Timor-Leste) | Sangat bergantung sama uploader. Ada yang beneran dari riset, ada yang asal upload. Lisensi bisa beda-beda | **Wajib cek per dataset** | **Perlu verifikasi** |
| **Plant Pathology (FGVC)** | [kaggle.com/competitions/plant-pathology-2020-fgvc7](https://www.kaggle.com/competitions/plant-pathology-2020-fgvc7) | Lebih mendekati lapangan | ~3.6k gambar | Gambar realistis, cukup menantang buat evaluasi | Fokus ke apel, bukan padi/jagung/ubi kayu yang jadi prioritas awal | Cek competition rules & data license | **Kurang relevan buat MVP awal** |

## 2. Rekomendasi Untuk MVP

Berdasarkan kebutuhan Agronia (fokus ke petani Timor-Leste), urutannya gini:

| Prioritas | Tanaman | Alasan |
|---|---|---|
| **#1** | **Padi (Oryza sativa)** | Makanan pokok di Timor-Leste, peluang dampak paling besar buat petani |
| **#2** | **Jagung (Zea mays)** | Cukup umum dibudidayakan, ada potensi dataset |
| **#3** | **Ubi Kayu (Manihot esculenta)** | Sangat umum, tapi dataset penyakitnya biasanya lebih terbatas |

**Rekomendasi:** Mulai dari **Padi saja** buat MVP pertama. Jangan langsung ambil 5-10 tanaman. Lebih baik **sedikit kelas, tapi bisa diuji dengan jujur** ketimbang banyak kelas tapi nggak relevan.

## 3. Rekomendasi Model

| Model | Bobot | Cocok Inference | Catatan |
|---|---|---|---|
| **MobileNetV2** | Ringan (~14MB) | Sangat cocok (CPU/server ringan) | Paling aman buat MVP. Transfer learning dari ImageNet. Cukup kuat buat baseline. |
| **EfficientNet-B0** | Sedang (~20MB) | Cocok | Akurasi biasanya lebih baik, masih bisa jalan di CPU. |
| **ResNet50** | Lebih berat (~98MB) | Kurang ideal awal | Akurasi bagus, tapi overkill buat mulai. Bisa dipertimbangkan nanti kalo perlu. |

**Rekomendasi awal:** **MobileNetV2 + ImageNet pretrained**. Ringan, gampang diintegrasi ke `ai/service/`, dan nggak makan resource berlebihan.

## 4. Langkah Selanjutnya

- [ ] **Verifikasi lisensi** - Buka halaman resmi PlantVillage & cek Terms/License. Jangan percaya cuma "free" di Kaggle.
- [ ] **Cari subset padi** - Kalo pakai PlantVillage, filter cuma kelas yang berhubungan sama padi. Catat nama kelas persis.
- [ ] **Mapping kelas** - Bandingin nama penyakit antara dataset vs yang mungkin relevan buat Timor-Leste.
- [ ] **Cek distribusi** - Lihat jumlah gambar per kelas. Hindari kelas dengan <20-30 gambar (rawan overfit).
- [ ] **Siapkan split** - Rencanain train/val/test (mis. 70/15/15) dengan stratified split.
- [ ] **Evaluasi realistis** - Ingat gap antara lab-image (PlantVillage) vs foto lapangan. Kita wajib catat ini di `ai-model.md`.

## Catatan Penting

- **Belum download apa-apa.** Semua poin di atas masih investigasi.
- **Jangan klaim akurasi** sebelum ada evaluasi terpisah di test set + dokumentasi metrik per kelas.
- **Fokus ke bukti**. Lisensi > hype popularitas dataset.
- **Kondisi lapangan beda**. PlantVillage bagus buat *proof of concept*, tapi perlu diuji dengan foto nyata dari Timor-Leste nanti.