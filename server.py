import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="Sistem Prediksi Harga Mobil Bekas",
    description="API Inferensi Kecerdasan Buatan menggunakan Random Forest Regressor",
    version="2.0.0"
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

# Melatih model Random Forest
df_encoded = pd.get_dummies(df, columns=["merek"])
X = df_encoded.drop("harga_juta", axis=1)
y = df_encoded["harga_juta"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Pre-kalkulasi statistik per merek
STATS_PER_MEREK: Dict[str, Dict[str, Any]] = {}
for m in DAFTAR_MEREK:
    sub = df[df["merek"] == m]
    STATS_PER_MEREK[m] = {
        "min_tahun": int(sub["tahun"].min()),
        "max_tahun": int(sub["tahun"].max()),
        "min_km": int(sub["kilometer"].min()),
        "max_km": int(sub["kilometer"].max()),
        "min_harga": int(sub["harga_juta"].min()),
        "max_harga": int(sub["harga_juta"].max()),
        "rata_harga": round(float(sub["harga_juta"].mean()), 1),
        "jumlah_data": int(len(sub)),
    }


class PredictRequest(BaseModel):
    merek: str = Field(..., description="Nama tipe/merek mobil")
    tahun: int = Field(..., ge=2010, le=2025, description="Tahun produksi mobil (2010 - 2025)")
    kilometer: int = Field(..., ge=0, le=500000, description="Jarak tempuh odometer (0 - 500.000 KM)")


class PredictResponse(BaseModel):
    status: str
    merek: str
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
        return FileResponse(index_file)
    return {"message": "Sistem Prediksi Harga Mobil Bekas siap. static/index.html belum dibuat."}


@app.get("/api/meta")
def get_metadata():
    return {
        "status": "success",
        "total_data": len(df),
        "total_merek": len(DAFTAR_MEREK),
        "daftar_merek": DAFTAR_MEREK,
        "statistik_merek": STATS_PER_MEREK,
        "rentang_tahun": [int(df["tahun"].min()), int(df["tahun"].max())],
    }


@app.post("/api/predict", response_model=PredictResponse)
def predict_price(req: PredictRequest):
    merek_clean = req.merek.strip().title()
    if merek_clean not in DAFTAR_MEREK:
        # Coba periksa kesamaan case insensitive
        matched = [m for m in DAFTAR_MEREK if m.lower() == merek_clean.lower()]
        if matched:
            merek_clean = matched[0]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Merek '{req.merek}' tidak terdaftar dalam basis pengetahuan. Pilihan tersedia: {', '.join(DAFTAR_MEREK)}"
            )

    # Siapkan vektor fitur sesuai skema training
    input_df = pd.DataFrame({"tahun": [req.tahun], "kilometer": [req.kilometer]})
    merek_enc = pd.get_dummies(pd.DataFrame({"merek": [merek_clean]}), columns=["merek"])
    input_df = pd.concat([input_df, merek_enc], axis=1).reindex(columns=X.columns, fill_value=0)

    # Ekstrak inferensi dari seluruh 100 pohon keputusan untuk analisis ketidakpastian
    input_values = input_df.values
    tree_predictions = np.array([tree.predict(input_values)[0] for tree in model.estimators_])
    mean_val = float(tree_predictions.mean())
    std_val = float(tree_predictions.std())

    # Toleransi harga wajar (interval kepercayaan estimasi)
    toleransi = max(std_val * 1.5, mean_val * 0.04)
    bawah_val = max(10.0, round(mean_val - toleransi, 1))
    atas_val = round(mean_val + toleransi, 1)

    # Cari 3 sampel pembanding terdekat dari dataset riil
    sub = df[df["merek"] == merek_clean].copy()
    sub["selisih_tahun"] = (sub["tahun"] - req.tahun).abs()
    sub["selisih_km"] = (sub["kilometer"] - req.kilometer).abs() / 10000.0
    sub["jarak_skor"] = sub["selisih_tahun"] * 2.0 + sub["selisih_km"]
    pembanding = sub.sort_values(by="jarak_skor").head(3)

    referensi_list = []
    for _, row in pembanding.iterrows():
        referensi_list.append({
            "merek": str(row["merek"]),
            "tahun": int(row["tahun"]),
            "kilometer": int(row["kilometer"]),
            "harga_juta": int(row["harga_juta"]),
            "harga_rupiah": format_rupiah(float(row["harga_juta"])),
        })

    return PredictResponse(
        status="success",
        merek=merek_clean,
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
def get_dataset(merek: str = None, limit: int = 100):
    filtered_df = df
    if merek:
        merek_clean = merek.strip().title()
        if merek_clean in DAFTAR_MEREK:
            filtered_df = df[df["merek"] == merek_clean]

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
        "total_merek": len(DAFTAR_MEREK)
    }

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)


