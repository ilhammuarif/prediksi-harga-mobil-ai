@echo off
title Server Prediksi Harga Mobil Bekas
cd /d "%~dp0"
echo ========================================================
echo   Menjalankan Server Web Prediksi Harga Mobil Bekas
echo   Otomatis membuka browser di: http://127.0.0.1:8000
echo ========================================================
start http://127.0.0.1:8000
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
