# Dataset Selection Checklist

Gunakan checklist ini setiap kali evaluasi kandidat dataset.

## Informasi Dasar
- [ ] **Nama dataset**: __________________
- [ ] **Sumber resmi** (URL): __________________
- [ ] **Publisher / Author**: __________________
- [ ] **Versi / Tanggal publikasi**: __________________
- [ ] **Download link**: __________________

## Lisensi & Legal
- [ ] **Lisensi ditemukan** (nama lisensi jelas)
- [ ] **Bisa dipakai untuk riset/prototipe** (ya/tidak + alasan)
- [ ] **Bisa dimodifikasi** (ya/tidak)
- [ ] **Butuh atribusi** (ya/tidak) - kalau iya, catat cara atribusinya
- [ ] **Bisa dipakai komersial?** (ya/tidak/tidak disebut) - untuk sekarang prototipe, tapi penting dicatat
- [ ] **Ada batasan lain** (ya/tidak + detail)

## Konten Dataset
- [ ] **Tanaman yang relevan**: __________________
- [ ] **Jumlah kelas total**: __________________
- [ ] **Daftar kelas (copy persis)**: __________________
- [ ] **Jumlah gambar per kelas** (minimal cek top 5 kelas)
- [ ] **Ada kelas "healthy"?** (ya/tidak)
- [ ] **Format gambar** (jpg/png/jpeg)
- [ ] **Resolusi rata-rata** (estimasi)
- [ ] **Label konsisten?** (ya/tidak + catatan)

## Kualitas & Realisme
- [ ] **Kondisi gambar** (lab / lapangan / campuran)
- [ ] **Background** (seragam / alami)
- [ ] **Pencahayaan** (terkontrol / bervariasi)
- [ ] **Mirip kondisi Timor-Leste?** (rendah/sedang/tinggi + alasan)
- [ ] **Ada duplikasi mencurigakan?** (dicek)
- [ ] **Ada noise/label salah?** (dicek sample 5-10 gambar)

## Kelayakan Teknis
- [ ] **Ukuran download** (MB/GB)
- [ ] **Cukup untuk CPU training/inference?** (ya/tidak)
- [ ] **Bisa diproses lokal?** (ya/tidak)
- [ ] **Perlu preprocessing khusus?** (ya/tidak + detail)

## Keputusan
- [ ] **Status**: ☐ Accept  ☐ Reject  ☐ Need More Info
- [ ] **Alasan keputusan**: __________________
- [ ] **Kelas MVP yang dipilih** (jika accept): __________________
- [ ] **Catatan untuk evaluasi nanti**: __________________

**Dicatat oleh:** __________________  
**Tanggal:** __________________
