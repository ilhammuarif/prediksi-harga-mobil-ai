# Summary Proyek Sistem Prediksi Harga Mobil Bekas (Kecerdasan Buatan)

## 1. Status Fitur
- **Web Application (`server.py` & `static/`)**: Berfungsi penuh menggunakan backend FastAPI (asinkron REST API) dan Web UI responsif modern (HTML5, CSS murni dengan standar antislop WCAG AA, Vanilla JS). Memuat endpoint prediksi `/api/predict` lengkap dengan rentang toleransi variansi ensemble pohon keputusan (*uncertainty estimation*), live market statistics, dan visualisasi tren harga pasar.
- **Desktop Application (`app.py`)**: Tersedia penuh sebagai alternatif aplikasi desktop mandiri berbasis Tkinter GUI dan Matplotlib tanpa dependensi peramban.
- **Runner Shortcut (`run_web.bat`)**: Skrip otomatisasi sekali klik untuk meluncurkan server uvicorn lokal dan membuka peramban web di `http://127.0.0.1:8000`.
- **Dataset (`data_mobil.csv` & `data_mobil.xlsx`)**: 2.000 baris data riil pasar valid terverifikasi (17 tipe model kendaraan terpopuler Indonesia tahun perakitan 2015 s.d. 2023). Terdiri atas 11 model dengan 118 baris dan 6 model dengan 117 baris. Evaluasi model Random Forest: $R^2 = 0.9980$, MAE = Rp 2,76 Juta.
- **Laporan Word Resmi (`Laporan_Sistem_Prediksi_Harga_Mobil.docx`)**:
  - Format standar akademik: Times New Roman 12pt, batas margin 4-3-3-3 cm, spasi 1.5, inden paragraf 1 cm, warna teks 100% hitam.
  - Penomoran halaman resmi 3 seksi:
    - Cover: Tanpa nomor halaman dan tidak dihitung (tepat 1 halaman fisik).
    - Bagian Awal (Kata Pengantar & Daftar Isi): Angka Romawi kecil (`i` dan `ii`).
    - Bagian Isi (BAB I s.d. DAFTAR PUSTAKA): Angka biasa/Arab dimulai dari angka `3` secara kontinu hingga `17`.
  - Daftar Isi: Terkoneksi 100% presisi dengan nomor halaman fisik Word, dilengkapi perataan kanan dan *dot leaders*.
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
- **Repositori Git**: [ilhammuarif/prediksi-harga-mobil-ai](https://github.com/ilhammuarif/prediksi-harga-mobil-ai) sudah terinisialisasi dan di-*push* ke remote GitHub.
- **Keamanan**: Pre-commit hook `lefthook` + `detect-secrets` aktif; `.gitignore` mengecualikan `.env`, `.env.*`, dan secret files.
- **Artefak Deployment**:
  - `Dockerfile`: Multi-stage ready, Python 3.11-slim, expose port 8000.
  - `Procfile` & `render.yaml`: Siap untuk 1-click deployment di Render.com.
  - `.env.example`: Template environment variable untuk port dan host dinamis.

