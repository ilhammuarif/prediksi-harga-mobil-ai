document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  const merekSelect = document.getElementById("merek-select");
  const tipeSelect = document.getElementById("tipe-select");
  const tipeHint = document.getElementById("tipe-hint");
  const tahunInput = document.getElementById("tahun-input");
  const kmInput = document.getElementById("km-input");
  const btnSubmit = document.getElementById("btn-submit");
  const btnText = document.getElementById("btn-text");
  const btnSpinner = document.getElementById("btn-spinner");
  const formError = document.getElementById("form-error");

  const emptyState = document.getElementById("empty-state");
  const loadingState = document.getElementById("loading-state");
  const successState = document.getElementById("success-state");

  const badgeMerek = document.getElementById("badge-merek");
  const badgeTipe = document.getElementById("badge-tipe");
  const badgeTahun = document.getElementById("badge-tahun");
  const badgeKm = document.getElementById("badge-km");
  const priceMain = document.getElementById("price-main");
  const priceRange = document.getElementById("price-range");
  const referenceList = document.getElementById("reference-list");

  const modelsTbody = document.getElementById("models-tbody");
  const searchInput = document.getElementById("table-search");

  let metadataCache = null;

  // --- Inisialisasi: Ambil Metadata Sistem ---
  async function loadMetadata() {
    try {
      const res = await fetch("/api/meta");
      if (!res.ok) throw new Error("Gagal memuat metadata sistem.");
      const data = await res.json();
      metadataCache = data;

      // Update Live Header Stats secara dinamis
      const statTotalData = document.getElementById("stat-total-data");
      const statTotalMerek = document.getElementById("stat-total-merek");
      const statTotalTipe = document.getElementById("stat-total-tipe");
      const statTotalTrees = document.getElementById("stat-total-trees");

      if (statTotalData && data.total_data) {
        statTotalData.textContent = formatNumber(data.total_data);
      }
      if (statTotalMerek && data.total_merek) {
        statTotalMerek.textContent = data.total_merek;
      }
      if (statTotalTipe && data.total_tipe) {
        statTotalTipe.textContent = data.total_tipe;
      }
      if (statTotalTrees && data.total_trees) {
        statTotalTrees.textContent = data.total_trees;
      }

      // Update Form Hint & Explorer Subtitle secara dinamis
      const merekHint = document.getElementById("merek-hint");
      if (merekHint && data.total_merek) {
        merekHint.textContent = `Tersedia ${data.total_merek} merek pabrikan bursa otomotif Indonesia.`;
      }
      const catalogSubtitle = document.getElementById("catalog-subtitle");
      if (catalogSubtitle && data.total_merek && data.total_tipe && data.total_data) {
        catalogSubtitle.textContent = `Ringkasan ${data.total_merek} kategori merek dan ${data.total_tipe} tipe mobil dalam basis data empiris ${formatNumber(data.total_data)} entri riil.`;
      }
      const footerSubtext = document.getElementById("footer-subtext");
      if (footerSubtext && data.total_data) {
        footerSubtext.textContent = `Sumber Data: Penjelajahan Web Terbuka Listing Otomotif Indonesia (Mobil123.com, Carmudi, OLX Autos) - ${formatNumber(data.total_data)} Baris Data Riil.`;
      }

      // Isi dropdown Kategori Merek
      merekSelect.innerHTML = '<option value="" disabled selected>Pilih kategori merek...</option>';
      data.daftar_merek.forEach((merek) => {
        const opt = document.createElement("option");
        opt.value = merek;
        opt.textContent = merek;
        merekSelect.appendChild(opt);
      });

      // Render tabel katalog model
      renderModelsTable(data.statistik_tipe);
    } catch (err) {
      showError("Koneksi ke backend gagal: " + err.message);
    }
  }

  // --- Relasi Hierarkis: Pilih Merek -> Tampilkan Tipe Mobil ---
  merekSelect.addEventListener("change", () => {
    const selectedMerek = merekSelect.value;
    if (!metadataCache || !metadataCache.kategori_merek) return;

    const availableModels = metadataCache.kategori_merek[selectedMerek] || [];
    tipeSelect.innerHTML = '<option value="" disabled selected>Pilih tipe mobil...</option>';
    
    availableModels.forEach((tipe) => {
      const opt = document.createElement("option");
      opt.value = tipe;
      opt.textContent = tipe;
      tipeSelect.appendChild(opt);
    });

    tipeSelect.disabled = false;
    if (tipeHint) {
      tipeHint.textContent = `Tersedia ${availableModels.length} tipe mobil untuk merek ${selectedMerek}.`;
    }
    tipeSelect.focus();
  });

  // --- Render Tabel Katalog ---
  function renderModelsTable(stats) {
    modelsTbody.innerHTML = "";
    Object.keys(stats).forEach((tipe) => {
      const item = stats[tipe];
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td><span class="brand-tag">${escapeHtml(item.merek)}</span></td>
        <td><strong>${escapeHtml(item.tipe)}</strong></td>
        <td>${item.min_tahun} - ${item.max_tahun}</td>
        <td>${formatNumber(item.min_km)} - ${formatNumber(item.max_km)} KM</td>
        <td>Rp ${item.min_harga} - ${item.max_harga} Juta</td>
        <td>Rp ${item.rata_harga} Juta</td>
        <td>${item.jumlah_data} baris</td>
        <td>
          <button type="button" class="table-btn" data-merek="${escapeHtml(item.merek)}" data-tipe="${escapeHtml(item.tipe)}">
            Pilih Model
          </button>
        </td>
      `;

      modelsTbody.appendChild(tr);
    });

    // Pasang listener pada tombol "Pilih Model" di tabel
    document.querySelectorAll(".table-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const targetMerek = e.currentTarget.getAttribute("data-merek");
        const targetTipe = e.currentTarget.getAttribute("data-tipe");
        
        merekSelect.value = targetMerek;

        if (metadataCache && metadataCache.kategori_merek) {
          const availableModels = metadataCache.kategori_merek[targetMerek] || [];
          tipeSelect.innerHTML = '<option value="" disabled selected>Pilih tipe mobil...</option>';
          availableModels.forEach((tipe) => {
            const opt = document.createElement("option");
            opt.value = tipe;
            opt.textContent = tipe;
            tipeSelect.appendChild(opt);
          });
          tipeSelect.disabled = false;
          if (tipeHint) {
            tipeHint.textContent = `Tersedia ${availableModels.length} tipe mobil untuk merek ${targetMerek}.`;
          }
        }
        tipeSelect.value = targetTipe;

        form.scrollIntoView({ behavior: "smooth", block: "start" });
        tahunInput.focus();
      });
    });
  }

  // --- Filter Pencarian Tabel (Bisa cari merek atau tipe) ---
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      const rows = modelsTbody.querySelectorAll("tr");
      rows.forEach((row) => {
        const brandName = row.cells[0]?.textContent.toLowerCase() || "";
        const modelName = row.cells[1]?.textContent.toLowerCase() || "";
        if (brandName.includes(query) || modelName.includes(query)) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }

  // --- Preset Chips Listener ---
  document.querySelectorAll("#tahun-presets .chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      tahunInput.value = chip.getAttribute("data-val");
      tahunInput.focus();
    });
  });

  document.querySelectorAll("#km-presets .chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      kmInput.value = chip.getAttribute("data-val");
      kmInput.focus();
    });
  });

  // --- Validasi & Submit Formulir Prediksi ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const merek = merekSelect.value;
    const tipe = tipeSelect.value;
    const tahun = parseInt(tahunInput.value, 10);
    const km = parseInt(kmInput.value, 10);

    // Validasi lokal
    if (!merek) {
      showError("Silakan pilih kategori merek pabrikan terlebih dahulu.");
      merekSelect.focus();
      return;
    }
    if (!tipe) {
      showError("Silakan pilih tipe / model mobil terlebih dahulu.");
      tipeSelect.focus();
      return;
    }
    if (isNaN(tahun) || tahun < 2010 || tahun > 2025) {
      showError("Tahun produksi harus berupa angka valid antara 2010 dan 2025.");
      tahunInput.focus();
      return;
    }
    if (isNaN(km) || km < 0) {
      showError("Jarak tempuh kilometer tidak boleh kosong atau bernilai negatif.");
      kmInput.focus();
      return;
    }

    // Set state memuat
    setLoading(true);

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          merek: merek,
          tipe: tipe,
          tahun: tahun,
          kilometer: km,
        }),
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error(result.detail || "Terjadi kesalahan inferensi pada server.");
      }

      displayResult(result);
    } catch (err) {
      showError(err.message);
      emptyState.style.display = "block";
      loadingState.style.display = "none";
      successState.style.display = "none";
    } finally {
      setLoading(false);
    }
  });

  // --- Tampilkan Hasil Prediksi ---
  function displayResult(data) {
    emptyState.style.display = "none";
    loadingState.style.display = "none";
    successState.style.display = "block";

    badgeMerek.textContent = data.merek;
    badgeTipe.textContent = data.tipe;
    badgeTahun.textContent = `Tahun ${data.tahun}`;
    badgeKm.textContent = `${formatNumber(data.kilometer)} KM`;

    priceMain.textContent = data.estimasi_rupiah;
    priceRange.textContent = `${data.rentang_bawah_rupiah} - ${data.rentang_atas_rupiah}`;

    // Render daftar pembanding riil
    referenceList.innerHTML = "";
    if (data.referensi_pasar && data.referensi_pasar.length > 0) {
      data.referensi_pasar.forEach((ref) => {
        const item = document.createElement("div");
        item.className = "ref-item";
        item.innerHTML = `
          <div class="ref-specs">
            <span class="ref-model">${escapeHtml(ref.merek)} ${escapeHtml(ref.tipe)} (${ref.tahun})</span>
            <span class="ref-meta">Odometer: ${formatNumber(ref.kilometer)} KM</span>
          </div>
          <div class="ref-price">${escapeHtml(ref.harga_rupiah)}</div>
        `;
        referenceList.appendChild(item);
      });
    }
  }

  // --- Helpers UI & Format ---
  function setLoading(isLoading) {
    if (isLoading) {
      btnSubmit.disabled = true;
      btnText.textContent = "Menghitung...";
      btnSpinner.style.display = "inline-block";
      emptyState.style.display = "none";
      successState.style.display = "none";
      loadingState.style.display = "block";
    } else {
      btnSubmit.disabled = false;
      btnText.textContent = "Hitung Estimasi Harga";
      btnSpinner.style.display = "none";
    }
  }

  function showError(msg) {
    formError.textContent = msg;
    formError.style.display = "block";
  }

  function hideError() {
    formError.textContent = "";
    formError.style.display = "none";
  }

  function formatNumber(num) {
    return Number(num).toLocaleString("id-ID");
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Jalankan inisialisasi awal
  loadMetadata();
});
