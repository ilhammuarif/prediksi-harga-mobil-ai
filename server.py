import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Sistem Prediksi Harga Mobil Bekas",
    description="API Inferensi Pembelajaran Mesin menggunakan Random Forest Regressor Berbasis Kategori Merek & Tipe Kendaraan",
    version="2.2.0"
)

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data_mobil.csv")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Memuat dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"File dataset tidak ditemukan di: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

DAFTAR_MEREK = sorted(df["merek"].unique().tolist())
DAFTAR_TIPE = sorted(df["tipe"].unique().tolist())

# Pemetaan relasi hierarkis Merek (Pabrikan) -> Tipe Mobil
KATEGORI_MEREK: Dict[str, List[str]] = {}
for m in DAFTAR_MEREK:
    KATEGORI_MEREK[m] = sorted(df[df["merek"] == m]["tipe"].unique().tolist())

TIPE_TO_MEREK: Dict[str, str] = dict(zip(df["tipe"], df["merek"]))

# Melatih Pipeline Random Forest
X = df[["merek", "tipe", "tahun", "kilometer"]]
y = df["harga_juta"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["merek", "tipe"]),
        ("num", "passthrough", ["tahun", "kilometer"])
    ]
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])
model.fit(X, y)

# Pre-kalkulasi statistik per tipe kendaraan
STATS_PER_TIPE: Dict[str, Dict[str, Any]] = {}
for t in DAFTAR_TIPE:
    sub = df[df["tipe"] == t]
    m_val = str(sub["merek"].iloc[0])
    STATS_PER_TIPE[t] = {
        "merek": m_val,
        "tipe": t,
        "min_tahun": int(sub["tahun"].min()),
        "max_tahun": int(sub["tahun"].max()),
        "min_km": int(sub["kilometer"].min()),
        "max_km": int(sub["kilometer"].max()),
        "min_harga": int(sub["harga_juta"].min()),
        "max_harga": int(sub["harga_juta"].max()),
        "rata_harga": round(float(sub["harga_juta"].mean()), 1),
        "jumlah_data": int(len(sub)),
    }

# Pre-kalkulasi statistik per kategori merek
STATS_PER_MEREK: Dict[str, Dict[str, Any]] = {}
for m in DAFTAR_MEREK:
    sub_m = df[df["merek"] == m]
    STATS_PER_MEREK[m] = {
        "merek": m,
        "total_model": len(KATEGORI_MEREK[m]),
        "total_data": int(len(sub_m)),
        "min_harga": int(sub_m["harga_juta"].min()),
        "max_harga": int(sub_m["harga_juta"].max()),
        "rata_harga": round(float(sub_m["harga_juta"].mean()), 1),
    }


class PredictRequest(BaseModel):
    merek: Optional[str] = Field(None, description="Nama merek pabrikan (misal: Toyota, Honda)")
    tipe: str = Field(..., description="Nama tipe/model mobil (misal: Avanza, Brio)")
    tahun: int = Field(..., ge=2010, le=2025, description="Tahun produksi mobil (2010 - 2025)")
    kilometer: int = Field(..., ge=0, le=500000, description="Jarak tempuh odometer (0 - 500.000 KM)")


class PredictResponse(BaseModel):
    status: str
    merek: str
    tipe: str
    tahun: int
    kilometer: int
    estimasi_juta: float
    estimasi_rupiah: str
    rentang_bawah_juta: float
    rentang_bawah_rupiah: str
    rentang_atas_juta: float
    rentang_atas_rupiah: str
    referensi_pasar: List[Dict[str, Any]]


def format_rupiah(nominal_juta: float) -> str:
    rupiah = int(round(nominal_juta * 1_000_000))
    return f"Rp {rupiah:,.0f}".replace(",", ".")


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return {"message": "Sistem Prediksi Harga Mobil Bekas siap. static/index.html belum dibuat."}


@app.get("/api/meta")
def get_metadata():
    return {
        "status": "success",
        "total_data": len(df),
        "total_merek": len(DAFTAR_MEREK),
        "total_tipe": len(DAFTAR_TIPE),
        "total_trees": 100,
        "daftar_merek": DAFTAR_MEREK,
        "daftar_tipe": DAFTAR_TIPE,
        "kategori_merek": KATEGORI_MEREK,
        "statistik_merek": STATS_PER_MEREK,
        "statistik_tipe": STATS_PER_TIPE,
        "rentang_tahun": [int(df["tahun"].min()), int(df["tahun"].max())],
    }


@app.post("/api/predict", response_model=PredictResponse)
def predict_price(req: PredictRequest):
    tipe_raw = req.tipe.strip()
    
    # Validasi dan resolusi tipe
    matched_tipe = [t for t in DAFTAR_TIPE if t.lower() == tipe_raw.lower()]
    if not matched_tipe:
        raise HTTPException(
            status_code=400,
            detail=f"Tipe mobil '{req.tipe}' tidak ditemukan. Pilihan tersedia: {', '.join(DAFTAR_TIPE)}"
        )
    tipe_clean = matched_tipe[0]
    
    # Resolusi merek otomatis bila tidak disertakan atau berbeda penulisan
    merek_clean = TIPE_TO_MEREK.get(tipe_clean, "Toyota")
    if req.merek:
        req_merek_clean = req.merek.strip().title()
        if req_merek_clean in DAFTAR_MEREK:
            # Periksa kecocokan merek dengan tipe
            if tipe_clean not in KATEGORI_MEREK.get(req_merek_clean, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipe '{tipe_clean}' bukan bagian dari kategori merek '{req_merek_clean}'. Model untuk {req_merek_clean}: {', '.join(KATEGORI_MEREK[req_merek_clean])}"
                )
            merek_clean = req_merek_clean

    # Siapkan DataFrame masukan untuk pipeline
    input_df = pd.DataFrame([{
        "merek": merek_clean,
        "tipe": tipe_clean,
        "tahun": req.tahun,
        "kilometer": req.kilometer
    }])

    # Transformasi dan inferensi ensemble pohon keputusan
    X_trans = model.named_steps["preprocessor"].transform(input_df)
    regressor = model.named_steps["regressor"]
    tree_predictions = np.array([tree.predict(X_trans)[0] for tree in regressor.estimators_])
    
    mean_val = float(tree_predictions.mean())
    std_val = float(tree_predictions.std())

    # Toleransi harga wajar (interval kepercayaan estimasi)
    toleransi = max(std_val * 1.5, mean_val * 0.04)
    bawah_val = max(10.0, round(mean_val - toleransi, 1))
    atas_val = round(mean_val + toleransi, 1)

    # Cari 3 sampel pembanding terdekat dari dataset riil
    sub = df[df["tipe"] == tipe_clean].copy()
    sub["selisih_tahun"] = (sub["tahun"] - req.tahun).abs()
    sub["selisih_km"] = (sub["kilometer"] - req.kilometer).abs() / 10000.0
    sub["jarak_skor"] = sub["selisih_tahun"] * 2.0 + sub["selisih_km"]
    pembanding = sub.sort_values(by="jarak_skor").head(3)

    referensi_list = []
    for _, row in pembanding.iterrows():
        referensi_list.append({
            "merek": str(row["merek"]),
            "tipe": str(row["tipe"]),
            "tahun": int(row["tahun"]),
            "kilometer": int(row["kilometer"]),
            "harga_juta": int(row["harga_juta"]),
            "harga_rupiah": format_rupiah(float(row["harga_juta"])),
        })

    return PredictResponse(
        status="success",
        merek=merek_clean,
        tipe=tipe_clean,
        tahun=req.tahun,
        kilometer=req.kilometer,
        estimasi_juta=round(mean_val, 1),
        estimasi_rupiah=format_rupiah(mean_val),
        rentang_bawah_juta=bawah_val,
        rentang_bawah_rupiah=format_rupiah(bawah_val),
        rentang_atas_juta=atas_val,
        rentang_atas_rupiah=format_rupiah(atas_val),
        referensi_pasar=referensi_list,
    )


@app.get("/api/dataset")
def get_dataset(merek: Optional[str] = None, tipe: Optional[str] = None, limit: int = 100):
    filtered_df = df
    if merek:
        m_clean = merek.strip().title()
        if m_clean in DAFTAR_MEREK:
            filtered_df = filtered_df[filtered_df["merek"] == m_clean]
    if tipe:
        t_clean = tipe.strip()
        matched = [t for t in DAFTAR_TIPE if t.lower() == t_clean.lower()]
        if matched:
            filtered_df = filtered_df[filtered_df["tipe"] == matched[0]]

    records = filtered_df.head(limit).to_dict(orient="records")
    return {
        "status": "success",
        "total_tersedia": len(filtered_df),
        "data": records
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "total_data": len(df),
        "total_merek": len(DAFTAR_MEREK),
        "total_tipe": len(DAFTAR_TIPE)
    }

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)
