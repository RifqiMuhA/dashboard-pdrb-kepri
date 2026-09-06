"""
Generator data CONTOH (sintetis) — hanya untuk demo/development dashboard.
Struktur sheet di sini adalah format "long/tidy" yang disarankan dipakai
untuk data ASLI kalian juga, karena jauh lebih mudah diolah di pandas
dibanding tabel lebar ala publikasi BPS.

Jalankan sekali: python data/generate_sample_data.py
Akan membuat file data/sample_data.xlsx
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

KAB_KOTA = ["Kab. Alfa", "Kab. Beta", "Kab. Gamma", "Kota Delta", "Kota Epsilon"]
LAPANGAN_USAHA = [
    "A. Pertanian, Kehutanan, dan Perikanan",
    "B. Pertambangan dan Penggalian",
    "C. Industri Pengolahan",
    "F. Konstruksi",
    "G. Perdagangan Besar dan Eceran",
    "R,S,T,U. Jasa Lainnya",
]
YEARS = list(range(2018, 2023))
PROVINSI = "Provinsi X"

# ---------------------------------------------------------------------------
# 1. PDRB ADHB & ADHK per kab/kota x lapangan usaha x tahun (+ level provinsi)
#    kolom: kab_kota, lapangan_usaha, tahun, adhb, adhk
# ---------------------------------------------------------------------------
rows = []
base_share = rng.dirichlet(np.ones(len(LAPANGAN_USAHA)) * 2, size=len(KAB_KOTA))

for i, kk in enumerate(KAB_KOTA):
    base_total_adhb = rng.uniform(15_000_000, 90_000_000)  # juta rupiah, tahun awal
    growth_rate = rng.uniform(0.03, 0.07, size=len(LAPANGAN_USAHA))
    for j, lu in enumerate(LAPANGAN_USAHA):
        val_adhb = base_total_adhb * base_share[i, j]
        val_adhk = val_adhb * rng.uniform(0.75, 0.95)
        for t_idx, tahun in enumerate(YEARS):
            shock = rng.normal(1, 0.015)
            val_adhb = val_adhb * (1 + growth_rate[j] * 1.4) * shock if t_idx > 0 else val_adhb
            val_adhk = val_adhk * (1 + growth_rate[j]) * shock if t_idx > 0 else val_adhk
            rows.append([kk, lu, tahun, round(val_adhb, 2), round(val_adhk, 2)])

df_pdrb = pd.DataFrame(rows, columns=["kab_kota", "lapangan_usaha", "tahun", "adhb", "adhk"])

# Tambahkan level provinsi = agregasi (jumlah) seluruh kab/kota
df_prov = (
    df_pdrb.groupby(["lapangan_usaha", "tahun"], as_index=False)[["adhb", "adhk"]]
    .sum()
)
df_prov.insert(0, "kab_kota", PROVINSI)
df_pdrb = pd.concat([df_pdrb, df_prov], ignore_index=True)

# ---------------------------------------------------------------------------
# 2. Penduduk per kab/kota x tahun (+ provinsi = total)
#    kolom: kab_kota, tahun, jumlah_penduduk
# ---------------------------------------------------------------------------
rows = []
for kk in KAB_KOTA:
    base_pop = rng.uniform(300_000, 1_800_000)
    for t_idx, tahun in enumerate(YEARS):
        base_pop = base_pop * rng.uniform(1.005, 1.02) if t_idx > 0 else base_pop
        rows.append([kk, tahun, round(base_pop)])
df_penduduk = pd.DataFrame(rows, columns=["kab_kota", "tahun", "jumlah_penduduk"])

df_pop_prov = df_penduduk.groupby("tahun", as_index=False)["jumlah_penduduk"].sum()
df_pop_prov.insert(0, "kab_kota", PROVINSI)
df_penduduk = pd.concat([df_penduduk, df_pop_prov], ignore_index=True)

# ---------------------------------------------------------------------------
# 3. Komponen pengeluaran — level PROVINSI saja (lazimnya tidak tersedia
#    per kab/kota di publikasi BPS)
#    kolom: tahun, uraian, adhb, adhk
# ---------------------------------------------------------------------------
uraian_pengeluaran = [
    "Konsumsi Rumah Tangga",
    "Konsumsi LNPRT",
    "Konsumsi Pemerintah",
    "PMTB",
    "Ekspor",
    "Impor",
]
rows = []
base_vals_adhb = {
    "Konsumsi Rumah Tangga": 180_000_000,
    "Konsumsi LNPRT": 3_000_000,
    "Konsumsi Pemerintah": 25_000_000,
    "PMTB": 90_000_000,
    "Ekspor": 60_000_000,
    "Impor": 70_000_000,
}
for uraian, base in base_vals_adhb.items():
    val_adhb = base
    val_adhk = base * 0.85
    for t_idx, tahun in enumerate(YEARS):
        g = rng.uniform(0.02, 0.06)
        if t_idx > 0:
            val_adhb *= (1 + g * 1.3)
            val_adhk *= (1 + g)
        rows.append([tahun, uraian, round(val_adhb, 2), round(val_adhk, 2)])
df_pengeluaran = pd.DataFrame(rows, columns=["tahun", "uraian", "adhb", "adhk"])

# ---------------------------------------------------------------------------
# 4. Pajak & Penerimaan SDA — level PROVINSI
#    kolom: tahun, penerimaan_pajak, penerimaan_sda
# ---------------------------------------------------------------------------
rows = []
pajak, sda = 12_000_000, 1_500_000
for t_idx, tahun in enumerate(YEARS):
    if t_idx > 0:
        pajak *= rng.uniform(1.03, 1.09)
        sda *= rng.uniform(0.95, 1.15)
    rows.append([tahun, round(pajak, 2), round(sda, 2)])
df_pajak = pd.DataFrame(rows, columns=["tahun", "penerimaan_pajak", "penerimaan_sda"])

# ---------------------------------------------------------------------------
# 5. Tenaga kerja per lapangan usaha x tahun — level PROVINSI
#    kolom: tahun, lapangan_usaha, jumlah_tenaga_kerja (ribu orang)
# ---------------------------------------------------------------------------
rows = []
base_tk = {lu: rng.uniform(80, 900) for lu in LAPANGAN_USAHA}
for lu, base in base_tk.items():
    val = base
    for t_idx, tahun in enumerate(YEARS):
        if t_idx > 0:
            val *= rng.uniform(0.97, 1.06)
        rows.append([tahun, lu, round(val, 1)])
df_tenaga_kerja = pd.DataFrame(rows, columns=["tahun", "lapangan_usaha", "jumlah_tenaga_kerja"])

# ---------------------------------------------------------------------------
# Simpan semua ke satu file Excel, 1 sheet per dataset
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    out_path = "data/sample_data.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_pdrb.to_excel(writer, sheet_name="pdrb", index=False)
        df_penduduk.to_excel(writer, sheet_name="penduduk", index=False)
        df_pengeluaran.to_excel(writer, sheet_name="pengeluaran_provinsi", index=False)
        df_pajak.to_excel(writer, sheet_name="pajak_provinsi", index=False)
        df_tenaga_kerja.to_excel(writer, sheet_name="tenaga_kerja_provinsi", index=False)
    print(f"Sample data tersimpan di: {out_path}")
