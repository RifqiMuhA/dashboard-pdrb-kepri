"""
Loader data untuk Dashboard PDRB.

CARA GANTI DENGAN DATA ASLI:
  1. Susun data asli kalian menjadi format long/tidy yang sama persis
     dengan skema di bawah.
  2. Simpan sebagai file CSV terpisah di dalam folder data/
     (contoh: data/pdrb.csv, data/penduduk.csv).
  3. Tidak perlu ubah kode di pages/ sama sekali.

Skema tiap sheet (kolom wajib ada, boleh ada kolom tambahan):
  - pdrb                  : kab_kota, lapangan_usaha, tahun, adhb, adhk
  - penduduk              : kab_kota, tahun, jumlah_penduduk
  - pengeluaran_provinsi  : tahun, uraian, adhb, adhk
  - pajak_provinsi        : tahun, penerimaan_pajak, penerimaan_sda
  - tenaga_kerja_provinsi : tahun, lapangan_usaha, jumlah_tenaga_kerja
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PROVINSI_LABEL = "Provinsi Kepulauan Riau"

KAB_KOTA_ORDER = [
    "Kabupaten Karimun",
    "Kabupaten Bintan",
    "Kabupaten Natuna",
    "Kabupaten Lingga",
    "Kabupaten Kepulauan Anambas",
    "Kota Batam",
    "Kota Tanjungpinang",
]


def load_all_data(data_dir: Path = DATA_DIR) -> dict:
    tables = [
        "pdrb",
        "penduduk",
        "perkapita",
        "sumber_pertumbuhan",
        "implisit",
        "pengeluaran_provinsi",
        "pajak_provinsi",
        "tenaga_kerja_provinsi",
    ]
    data = {}
    for table in tables:
        csv_path = data_dir / f"{table}.csv"
        if csv_path.exists():
            data[table] = pd.read_csv(csv_path)
        else:
            data[table] = pd.DataFrame()
    return data


# Dimuat sekali saat aplikasi start, dipakai lintas halaman (import DATA dari sini)
DATA = load_all_data()


def get_kab_kota_list(exclude_provinsi: bool = True) -> list:
    df = DATA.get("pdrb", pd.DataFrame())
    if df.empty or "kab_kota" not in df.columns:
        return [kk for kk in KAB_KOTA_ORDER if not exclude_provinsi or kk != PROVINSI_LABEL]
    
    unique_kk = df["kab_kota"].unique().tolist()
    # Urutkan berdasarkan urutan resmi KAB_KOTA_ORDER
    ordered = [kk for kk in KAB_KOTA_ORDER if kk in unique_kk]
    # Sisa jika ada wilayah lain
    for kk in sorted(unique_kk):
        if kk not in ordered and (not exclude_provinsi or kk != PROVINSI_LABEL):
            ordered.append(kk)
    if not exclude_provinsi and PROVINSI_LABEL in unique_kk and PROVINSI_LABEL not in ordered:
        ordered.append(PROVINSI_LABEL)
    return ordered


def get_lapangan_usaha_list() -> list:
    df = DATA.get("pdrb", pd.DataFrame())
    if df.empty or "lapangan_usaha" not in df.columns:
        return []
    return sorted(df["lapangan_usaha"].unique().tolist())


def get_years_list() -> list:
    df = DATA.get("pdrb", pd.DataFrame())
    if df.empty or "tahun" not in df.columns:
        return [2021, 2022, 2023, 2024, 2025]
    return sorted(df["tahun"].unique().tolist())
