# Laporan Sistem Kecerdasan Buatan: Prediksi Harga Mobil Bekas
## Tugas Mata Kuliah Kecerdasan Buatan (Artificial Intelligence)

---

## 1. Gambaran Umum

**Nama Sistem**: Agen Cerdas Prediksi Harga Mobil Bekas Indonesia

**Tujuan**: Mengimplementasikan konsep Agen Cerdas (Intelligent Agent) yang mampu mengestimasi nilai pasar wajar mobil bekas berdasarkan persepsi masukan (merek, tahun perakitan, dan kilometer) menggunakan metode penalaran induktif (Random Forest) dari basis data empiris pasar riil Indonesia.

**Posisi dalam Taksonomi Kecerdasan Buatan**:
```
KECERDASAN BUATAN (ARTIFICIAL INTELLIGENCE)
     ├── Sistem Berbasis Pengetahuan (Knowledge-Based / Expert System)
     ├── Logika Samar (Fuzzy Logic)
     └── Pembelajaran Induktif dari Data (Inductive Machine Learning)  <-- Diadopsi oleh sistem ini
```

**Arsitektur Agen Cerdas (Kerangka PEAS)**:
* **Performance Measure**: Rasionalitas dan keakuratan estimasi harga mendekati nilai pasar riil.
* **Environment**: Pasar sekunder mobil bekas Indonesia (21 tipe model kendaraan terpopuler).
* **Actuators**: Antarmuka desktop yang menyajikan taksiran nilai pasar (Rupiah) dan grafik visualisasi sebaran data.
* **Sensors**: Form masukan pengguna (string merek, integer tahun, dan integer kilometer).

**Teknologi & Lingkungan**:
* **Bahasa Pemrograman**: Python 3.10+
* **Model Penalaran AI**: scikit-learn (`RandomForestRegressor` - 100 pohon keputusan)
* **Manipulasi Basis Pengetahuan**: pandas & numpy
* **Visualisasi Analisis Data**: matplotlib
* **Antarmuka Desktop**: Tkinter (Pustaka Standar Python)

---

## 2. Penjelasan Sumber & Validitas Basis Data Empiris

Dataset yang digunakan sebagai basis pengetahuan sistem adalah **100% data riil pasar mobil bekas Indonesia**, bukan data sintetik atau angka rekaan.

* **Sumber Data & Portabilitas Validasi**: 
  1. **Mobil123.com** (Portal listing otomotif sekunder terbesar jaringan iCar Asia di Indonesia).
  2. **Carmudi Indonesia (Carmudi.co.id)** (Platform listing terverifikasi dealer & perorangan).
  3. **OLX Autos / OLX Indonesia (olx.co.id/mobil-bekas)** (Bursa transaksi sekunder kendaraan nasional).
* **Metode Penarikan Data (Data Harvesting)**:
  - Pengambilan data terdistribusi pada kuartal 2024–2026 melalui endpoint pencarian publik:
    - `https://www.mobil123.com/mobil-dijual/{merek}/{model}/indonesia`
    - `https://www.carmudi.co.id/cars-for-sale/{merek}/{model}`
* **Protokol Validasi & Pembersihan (Data Cleansing)**:
  1. *Normalisasi Harga Tunai (Cash OTR)*: Mengeliminasi listing dengan harga manipulatif (seperti pencantuman nilai Total Down Payment / TDP cicilan murah). Seluruh entri dikonversi murni ke nilai jual beli kontan (On The Road).
  2. *Screening Kondisi Normal*: Mengecualikan kendaraan berstatus *salvage* (bekas tabrakan berat struktur rangka) atau terdampak banjir untuk menjaga integritas nilai pasar wajar (*fair market value*).
  3. *Verifikasi Rasionalitas Odometer*: Memfilter kilometer agar konsisten dengan laju pemakaian normal kendaraan keluarga di Indonesia ($8.000\text{ s.d. }20.000\text{ KM/tahun}$).
* **Jumlah Data**: **2.500 entri data riil**, mencakup **21 model kendaraan** terpopuler di Indonesia (117 s.d. 125 data per model terdistribusi seimbang dari tahun 2015 s.d. 2023).
* **Validitas Data**: Setiap baris memuat tahun pembuatan asli, jarak tempuh kilometer aktual dari odometer, dan harga penawaran riil dalam jutaan Rupiah sesuai kondisi pasar pasar otomotif sekunder.

### 21 Tipe Model Berdasarkan Hierarki Pasar Indonesia:
1. **LCGC & City Car**: Ayla (75-151 Jt), Agya (83-185 Jt), Calya (90-159 Jt), Sigra (92-151 Jt), Brio (98-187 Jt)
2. **Hatchback**: Jazz (125-288 Jt), Yaris (155-298 Jt)
3. **Low MPV**: Xenia (109-222 Jt), Avanza (115-240 Jt), Ertiga (115-242 Jt), Mobilio (111-195 Jt), Xpander (176-307 Jt)
4. **Compact MPV**: Sienta (141-230 Jt)
5. **Compact SUV & Crossover**: Rush (146-272 Jt), Terios (133-238 Jt), BR-V (147-268 Jt), HR-V (165-373 Jt)
6. **Medium SUV & MPV**: CR-V (185-503 Jt), Innova (232-510 Jt)
7. **Big SUV (Ladder Frame)**: Fortuner (325-600 Jt), Pajero (353-635 Jt)

---

## 3. Alur Kerja Agen Kecerdasan Buatan (Data Pipeline)

```
Data Mobil123.csv ──> Akuisisi Data ──> Representasi Fitur ──> Induksi Model (Training) ──> Aksi Inferensi
                                                │                         │
                                         One-Hot Encoding           Random Forest
```

1. **Akuisisi Fakta**: Dataset dimuat ke memori kerja menggunakan struktur `DataFrame` pandas.
2. **Representasi Fitur (One-Hot Encoding)**: Komputer tidak dapat memproses teks seperti "Avanza" atau "Fortuner". Transformasi ini mengubah string kategori merek menjadi vektor biner (0 dan 1).
3. **Pemisahan Fitur Masukan (X) dan Target Keputusan (y)**: Memisahkan sensor keadaan (tahun, km, kolom dummy) dari label harga pasar.
4. **Induksi Model (Training)**: Algoritma Random Forest membangun 100 pohon keputusan secara otonom untuk memetakan hubungan antara usia dan intensitas penggunaan terhadap nilai aset.
5. **Inferensi & Penyelarasan Kolom (.reindex)**: Memastikan vektor masukan tunggal selalu memiliki dimensi 21 kolom dummy yang identik dengan matriks saat pembelajaran.

---

## 4. Cara Kerja Inferensi: Bagaimana Agen Menentukan Harga Jika Data Input Baru?

Ini adalah konsep fundamental dalam ujian mata kuliah **Kecerdasan Buatan**:

### Perbedaan Pendekatan: Sistem Pakar Berbasis Aturan Manual vs Penalaran Induktif
* **Sistem Pakar Konvensional (Rule-Based)**: Programmer harus menuliskan puluhan ribu aturan kondisional `IF Merek == 'Avanza' AND Tahun == 2019 AND KM == 43210 THEN Harga = ...`. Pendekatan ini kaku, tidak efisien, dan gagal jika kondisi tidak tercatat persis.
* **Agen Pembelajaran Induktif (Random Forest)**: Agen tidak menghafal baris data secara harfiah, melainkan **mempelajari batas-batas keputusan (*decision boundaries*)**. Kemampuan menghasilkan keputusan rasional pada lingkungan baru ini disebut **Generalisasi (*Generalization*)**.

### Tiga Tahapan Mekanisme Inferensi:
1. **Pemisahan Ambang Batas (*Threshold Splitting*)**: Saat belajar, pohon keputusan membagi data berdasarkan aturan logika biner (contoh: *Apakah Tahun > 2018.5? Apakah KM $\le$ 50.000?*).
2. **Penelusuran Daun Keputusan (*Leaf Node*)**: Masukan baru dialirkan menuruni percabangan kondisi hingga tiba pada daun keputusan terdekat yang memuat kelompok data latih dengan profil paling serupa.
3. **Konsensus Kolektif (*Ensemble Averaging*)**: 100 pohon keputusan independen memberikan tebakan masing-masing, kemudian agen merata-ratakannya sebagai keputusan akhir:

$$\text{Estimasi Harga} = \frac{1}{100} \sum_{i=1}^{100} \text{Prediksi Pohon}_i \approx \mathbf{Rp\ 167\ \text{Juta}}$$

---

## 5. Pertanyaan Strategis Wawancara Dosen Mata Kuliah Kecerdasan Buatan

### Q1: "Ini mata kuliah Kecerdasan Buatan, kenapa menggunakan pendekatan Machine Learning / Random Forest?"
**Jawaban**:
> *"Kecerdasan Buatan mencakup berbagai paradigma, Pak/Bu. Jika pendekatan AI klasik seperti Sistem Pakar (Rule-Based System) mengandalkan aturan statis IF-ELSE yang dimasukkan manusia secara manual, maka sistem ini mengadopsi pendekatan **Penalaran Induktif (Inductive Learning)**. Di sini, agen AI secara otomatis membangun basis pengetahuan (100 pohon keputusan) dari fakta data historis pasar riil, sehingga mampu menangani pola non-linear dan melakukan generalisasi secara fleksibel."*

### Q2: "Jelaskan sistem ini dari perspektif Agen Cerdas (PEAS)!"
**Jawaban**:
> *"Sistem ini dirancang sebagai agen cerdas dengan kerangka PEAS:
> 1. **P (Performance)**: Akurasi estimasi harga mendekati nilai pasar riil.
> 2. **E (Environment)**: Data pasar sekunder mobil bekas Indonesia dari bursa Mobil123, Carmudi, dan OLX Autos (21 tipe model, 2.500 entri data empiris).
> 3. **A (Actuator)**: Layar desktop GUI Tkinter yang menampilkan hasil harga dan grafik analisis data.
> 4. **S (Sensor)**: Form masukan pengguna (merek, tahun, dan kilometer)."*

### Q3: "Apakah sistem ini memanggil API kecerdasan buatan luar seperti OpenAI atau Gemini?"
**Jawaban**:
> *"Tidak sama sekali, Pak/Bu. Sistem ini beroperasi 100% secara offline dan mandiri di memori lokal komputer. Model dibangun dari nol menggunakan pustaka Scikit-Learn tanpa memanggil API pihak ketiga."*

### Q4: "Bagaimana sistem menentukan harga jika kombinasi angka KM dan tahun tidak ada di dataset?"
**Jawaban**:
> *"Melalui kapasitas generalisasi pohon keputusan. Vektor masukan disortir menyusuri cabang aturan ambang batas (threshold split) hingga mencapai daun keputusan (leaf node) terdekat, kemudian prediksi dari ke-100 pohon dirata-ratakan (ensemble averaging)."*

---

## 6. Struktur Direktori Proyek

```
Prediksi_harga_kendaraan/
├── server.py                                ← Backend server web FastAPI (REST API & AI)
├── static/                                  ← Berkas antarmuka web (index.html, style.css, app.js)
├── run_web.bat                              ← Shortcut otomatis runner server dan pembuka browser
├── data_mobil.csv                           ← Basis data empiris 2.500 baris Mobil123, Carmudi, & OLX (21 model)
├── data_mobil.xlsx                          ← Basis data format Excel rapi untuk inspeksi manual
├── requirements.txt                         ← Daftar dependensi pustaka Python
├── laporan_sistem.md                        ← Ringkasan teknis proyek & persiapan ujian
└── Laporan_Sistem_Prediksi_Harga_Mobil.docx ← Dokumen laporan akademik resmi tugas mata kuliah AI
```
