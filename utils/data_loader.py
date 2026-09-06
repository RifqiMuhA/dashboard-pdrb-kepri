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

PROVINSI_LABEL = "Provinsi X"  # sesuaikan dengan label provinsi di data kalian


def load_all_data(data_dir: Path = DATA_DIR) -> dict:
    tables = ["pdrb", "penduduk", "pengeluaran_provinsi", "pajak_provinsi", "tenaga_kerja_provinsi"]
    data = {}
    for table in tables:
        csv_path = data_dir / f"{table}.csv"
        data[table] = pd.read_csv(csv_path)
    return data


# Dimuat sekali saat aplikasi start, dipakai lintas halaman (import DATA dari sini)
DATA = load_all_data()


def get_kab_kota_list(exclude_provinsi: bool = True) -> list:
    df = DATA["pdrb"]
    kk = sorted(df["kab_kota"].unique().tolist())
    if exclude_provinsi and PROVINSI_LABEL in kk:
        kk.remove(PROVINSI_LABEL)
    return kk


def get_lapangan_usaha_list() -> list:
    return sorted(DATA["pdrb"]["lapangan_usaha"].unique().tolist())


def get_years_list() -> list:
    return sorted(DATA["pdrb"]["tahun"].unique().tolist())
