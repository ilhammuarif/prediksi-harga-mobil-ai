import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestRegressor

# --- Muat Data dan Latih Model ---

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_mobil.csv")
df = pd.read_csv(DATA_PATH)

df_encoded = pd.get_dummies(df, columns=["merek"])
X = df_encoded.drop("harga_juta", axis=1)
y = df_encoded["harga_juta"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

DAFTAR_MEREK = sorted(df["merek"].unique())


# --- Fungsi Prediksi ---

def prediksi():
    merek = entry_merek.get().strip().title()
    tahun_str = entry_tahun.get().strip()
    km_str = entry_km.get().strip()

    if not merek:
        messagebox.showerror("Error", "Nama merek tidak boleh kosong.")
        return
    if merek not in DAFTAR_MEREK:
        messagebox.showerror(
            "Error",
            f'Merek "{merek}" tidak ditemukan dalam dataset.\n\n'
            f"Merek yang tersedia:\n{', '.join(DAFTAR_MEREK)}",
        )
        return

    try:
        tahun = int(tahun_str)
    except ValueError:
        messagebox.showerror("Error", "Tahun harus berupa angka.\nContoh: 2020")
        return
    try:
        km = int(km_str)
    except ValueError:
        messagebox.showerror("Error", "Kilometer harus berupa angka.\nContoh: 50000")
        return

    if tahun < 2010 or tahun > 2025:
        messagebox.showerror("Error", "Tahun harus antara 2010 dan 2025.")
        return
    if km < 0:
        messagebox.showerror("Error", "Kilometer tidak boleh negatif.")
        return

    # Susun input sesuai format training
    input_df = pd.DataFrame({"tahun": [tahun], "kilometer": [km]})
    merek_enc = pd.get_dummies(
        pd.DataFrame({"merek": [merek]}), columns=["merek"]
    )
    input_df = pd.concat([input_df, merek_enc], axis=1)
    input_df = input_df.reindex(columns=X.columns, fill_value=0)

    harga = model.predict(input_df)[0]

    label_hasil.config(text=f"Estimasi Harga: Rp {harga:,.0f} Juta")
    label_detail.config(text=f"{merek} tahun {tahun}, jarak tempuh {km:,} KM")


# --- Fungsi Tampilkan Grafik ---

def tampilkan_grafik():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Box plot harga per merek
    df.boxplot(column="harga_juta", by="merek", ax=ax1)
    ax1.set_xlabel("Merek")
    ax1.set_ylabel("Harga (Juta Rp)")
    ax1.set_title("Distribusi Harga per Merek")
    plt.sca(ax1)
    plt.xticks(rotation=45)

    # Scatter plot tahun vs harga
    for merek in DAFTAR_MEREK:
        subset = df[df["merek"] == merek]
        ax2.scatter(subset["tahun"], subset["harga_juta"], label=merek, alpha=0.7, s=45)
    ax2.set_xlabel("Tahun Produksi")
    ax2.set_ylabel("Harga (Juta Rp)")
    ax2.set_title("Tahun Produksi vs Harga")
    ax2.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)

    fig.suptitle("")
    plt.tight_layout()
    plt.show()


# --- Bangun Tampilan GUI ---

root = tk.Tk()
root.title("Sistem Prediksi Harga Mobil Bekas")
root.geometry("750x700")
root.resizable(False, False)

# Judul
tk.Label(
    root, text="Prediksi Harga Mobil Bekas", font=("Arial", 18, "bold")
).pack(pady=(15, 5))
tk.Label(
    root, text="Sistem Kecerdasan Buatan (21 Tipe Kendaraan, 2.500 Data Pasar)", font=("Arial", 10), fg="gray"
).pack()

# --- Tabel Merek ---
frame_info = ttk.LabelFrame(root, text="Merek Mobil dalam Dataset (Gunakan scroll untuk melihat semua)")
frame_info.pack(padx=20, pady=(15, 5), fill="x")

tree_container = ttk.Frame(frame_info)
tree_container.pack(padx=10, pady=5, fill="x")

kolom_tabel = ("Merek", "Tahun", "Harga (Juta Rp)", "Jumlah Data")
tree = ttk.Treeview(tree_container, columns=kolom_tabel, show="headings", height=6)

scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

lebar = {"Merek": 130, "Tahun": 150, "Harga (Juta Rp)": 200, "Jumlah Data": 110}
for col in kolom_tabel:
    tree.heading(col, text=col)
    tree.column(col, width=lebar[col], anchor="center")

for merek in DAFTAR_MEREK:
    subset = df[df["merek"] == merek]
    tree.insert("", "end", values=(
        merek,
        f"{subset['tahun'].min()} - {subset['tahun'].max()}",
        f"Rp {subset['harga_juta'].min()} - {subset['harga_juta'].max()}",
        len(subset),
    ))

tree.pack(side="left", fill="x", expand=True)
scrollbar.pack(side="right", fill="y")

# Tombol grafik
tk.Button(
    frame_info, text="Lihat Grafik Data", command=tampilkan_grafik
).pack(pady=(0, 8))

# --- Form Input ---
frame_input = ttk.LabelFrame(root, text="Masukkan Data Mobil")
frame_input.pack(padx=20, pady=10, fill="x")

tk.Label(frame_input, text="Merek Mobil:").grid(
    row=0, column=0, padx=10, pady=8, sticky="w"
)
entry_merek = tk.Entry(frame_input, width=25, font=("Arial", 11))
entry_merek.grid(row=0, column=1, padx=10, pady=8)
tk.Label(frame_input, text="Contoh: Avanza", fg="gray").grid(
    row=0, column=2, padx=5, sticky="w"
)

tk.Label(frame_input, text="Tahun Produksi:").grid(
    row=1, column=0, padx=10, pady=8, sticky="w"
)
entry_tahun = tk.Entry(frame_input, width=25, font=("Arial", 11))
entry_tahun.grid(row=1, column=1, padx=10, pady=8)
tk.Label(frame_input, text="Contoh: 2020", fg="gray").grid(
    row=1, column=2, padx=5, sticky="w"
)

tk.Label(frame_input, text="Jarak Tempuh (KM):").grid(
    row=2, column=0, padx=10, pady=8, sticky="w"
)
entry_km = tk.Entry(frame_input, width=25, font=("Arial", 11))
entry_km.grid(row=2, column=1, padx=10, pady=8)
tk.Label(frame_input, text="Contoh: 50000", fg="gray").grid(
    row=2, column=2, padx=5, sticky="w"
)

# Tombol prediksi
tk.Button(
    frame_input,
    text="Prediksi Harga",
    command=prediksi,
    font=("Arial", 12, "bold"),
    bg="#3B7DD8",
    fg="white",
    padx=20,
    pady=5,
    cursor="hand2",
).grid(row=3, column=0, columnspan=3, pady=12)

# --- Hasil Prediksi ---
frame_hasil = ttk.LabelFrame(root, text="Hasil Prediksi")
frame_hasil.pack(padx=20, pady=(5, 15), fill="x")

label_hasil = tk.Label(
    frame_hasil, text="Masukkan data mobil lalu klik Prediksi Harga",
    font=("Arial", 14, "bold"), fg="gray"
)
label_hasil.pack(pady=(10, 2))

label_detail = tk.Label(frame_hasil, text="", font=("Arial", 10), fg="gray")
label_detail.pack(pady=(0, 10))

root.mainloop()
