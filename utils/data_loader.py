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
    table_files = {
        "pdrb": "pdrb.csv",
        "penduduk": "penduduk.csv",
        "perkapita": "perkapita.csv",
        "sumber_pertumbuhan": "sumber_pertumbuhan.csv",
        "implisit": "implisit.csv",
        "konsumsi_apc_mpc": "konsumsi_apc_mpc.csv",
        "icor": "icor.csv",
        "ilor_etk": "ilor_etk.csv",
        "tax_ratio": "tax_ratio.csv",
        "perdagangan_internasional": "perdagangan_internasional.csv",
        "shift_share_kk": "shift_share_kabupaten_kota_2021_2025.csv",
        "shift_share_prov": "shift_share_provinsi_kepri_2021_2025.csv",
        "lq_kk": "lq_kabupaten_kota_2021_2025.csv",
        "lq_prov": "lq_provinsi_kepri_2021_2025.csv",
        "williamson_bonet_kepri": "williamson_bonet_kepri.csv",
        "williamson_bonet_sumatera": "williamson_bonet_sumatera.csv",
    }
    data = {}
    for key, filename in table_files.items():
        csv_path = data_dir / filename
        if csv_path.exists():
            data[key] = pd.read_csv(csv_path)
        else:
            data[key] = pd.DataFrame()
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
