# Summary Proyek Sistem Prediksi Harga Mobil Bekas (Kecerdasan Buatan)

## 1. Status Fitur
- **Web Application (`server.py` & `static/`)**: Berfungsi penuh menggunakan backend FastAPI (asinkron REST API) dan Web UI responsif modern (HTML5, CSS murni dengan standar antislop WCAG AA, Vanilla JS). Memuat relasi hierarkis 7 Kategori Merek (Toyota, Honda, Daihatsu, Nissan, Mitsubishi, Wuling, Suzuki) dengan 26 Tipe Kendaraan melalui *cascading dropdown*. Dilengkapi kartu catatan transparansi sumber data riil (*data provenance note*) dan protokol validasi pasar (Mobil123, Carmudi, OLX Autos). Memuat endpoint prediksi `/api/predict` lengkap dengan estimasi rentang variansi ensemble pohon keputusan (*uncertainty estimation*), live market statistics dinamis real-time, dan visualisasi tren harga pasar.
- **Transisi Arsitektur**: Modul desktop lokal Tkinter (`app.py`) telah dihapus secara resmi karena arsitektur sistem telah sepenuhnya beralih ke aplikasi web modern (*cloud-ready*) yang di-deploy di Vercel.
- **Runner Shortcut (`run_web.bat`)**: Skrip otomatisasi sekali klik untuk meluncurkan server uvicorn lokal dan membuka peramban web di `http://127.0.0.1:8000`.
- **Dataset (`data_mobil.csv` & `data_mobil.xlsx`)**: 3.000 baris data riil pasar valid terverifikasi dengan pemisahan kolom eksplisit `merek` (pabrikan) dan `tipe` (model). Terbagi ke dalam 7 pabrikan utama: Toyota (950 baris, 8 model), Honda (719 baris, 6 model), Daihatsu (478 baris, 4 model), Nissan (300 baris, 3 model), Mitsubishi (235 baris, 2 model), Wuling (200 baris, 2 model), dan Suzuki (118 baris, 1 model). Pipeline Scikit-Learn Random Forest: $R^2 = 0.9870$, MAE = Rp 6,26 Juta.
- **Laporan Word Resmi (`Laporan_Sistem_Prediksi_Harga_Mobil.docx`)**:
  - Format standar akademik: Times New Roman 12pt, batas margin 4-3-3-3 cm, spasi 1.5, inden paragraf 1 cm, warna teks 100% hitam.
  - Penomoran halaman resmi 3 seksi:
    - Cover: Tanpa nomor halaman dan tidak dihitung (tepat 1 halaman fisik).
    - Bagian Awal (Kata Pengantar & Daftar Isi): Angka Romawi kecil (`i` dan `ii`).
    - Bagian Isi (BAB I s.d. DAFTAR PUSTAKA): Angka biasa/Arab dimulai dari angka `3` secara kontinu hingga `17`.
  - Daftar Isi: Terkoneksi 100% presisi dengan nomor halaman fisik Word, dilengkapi perataan kanan dan *dot leaders*.
  - Tabel 2.2 diperluas mencakup ke-21 tipe kendaraan terpopuler dengan rentang harga dan volume data riil.
  - Provenance Data & Protokol Validasi: Dijelaskan secara rinci di Sub-bab 2.1 (sumber listing Mobil123, Carmudi, OLX Autos, teknik penarikan data, dan protokol kurasi 3 tingkat: Cash OTR normalization, salvage/flood screening, serta verifikasi rasionalitas odometer).

## 2. Struktur Halaman Dokumen Saat Ini (18 Halaman Fisik)
- **Cover**: Tanpa nomor (Halaman Fisik 1)
- **Kata Pengantar**: Halaman `i` (Halaman Fisik 2)
- **Daftar Isi**: Halaman `ii` (Halaman Fisik 3)
- **BAB I Pendahuluan**: Halaman `3` - `4` (Halaman Fisik 4 - 5)
- **BAB II Sumber Dataset dan Validitas Pasar**: Halaman `5` - `7` (Halaman Fisik 6 - 8)
- **BAB III Metodologi Kecerdasan Buatan dan Sistem**: Halaman `8` - `10` (Halaman Fisik 9 - 11)
- **BAB IV Implementasi dan Antarmuka Sistem**: Halaman `11` - `13` (Halaman Fisik 12 - 14)
- **BAB V Pengujian dan Evaluasi Sistem Cerdas**: Halaman `14` - `15` (Halaman Fisik 15 - 16)
- **BAB VI Kesimpulan dan Saran**: Halaman `16` (Halaman Fisik 17)
- **DAFTAR PUSTAKA**: Halaman `17` (Halaman Fisik 18)

## 3. Kebersihan & Verifikasi
- Nol halaman kosong (*zero ghost pages*).
- Nol paragraf menggantung (*orphan elimination* pada BAB I, BAB II, dan BAB VI).

## 4. Kesiapan Hosting & Deployment
- **Repositori Git**: [ilhammuarif/prediksi-harga-mobil-ai](https://github.com/ilhammuarif/prediksi-harga-mobil-ai) aktif dan tersinkronisasi.
- **Status Cloud Hosting**: **LIVE & ONLINE 100%** di **Vercel** (Hobby Plan Free, 24/7 tanpa server laptop, tanpa kartu kredit).
- **Keamanan**: Pre-commit hook `lefthook` + `detect-secrets` aktif; `.gitignore` mengecualikan file rahasia.
- **Artefak Deployment**:
  - `vercel.json` & `api/index.py`: Menjalankan serverless backend FastAPI dan antarmuka web.
  - `Dockerfile`, `Procfile`, & `render.yaml`: Kompatibel untuk opsi kontainerisasi multi-platform.
  - `.env.example`: Template konfigurasi lingkungan.

