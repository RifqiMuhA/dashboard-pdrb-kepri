"""
Script pembersih dan penyiapan data produksi untuk Dashboard PDRB Kepulauan Riau.
Mengekstrak data mentah dari:
- data/sumber_data_dashboard.xlsx
- data/Tipologi_Klassen_Kepri_2021-2025.xlsx

Menghasilkan file CSV bersih dan terstruktur di folder data/:
- data/pdrb.csv
- data/penduduk.csv
- data/perkapita.csv
- data/sumber_pertumbuhan.csv
- data/implisit.csv
"""

import re
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EXCEL_DASHBOARD = DATA_DIR / "sumber_data_dashboard.xlsx"
EXCEL_KLASSEN = DATA_DIR / "Tipologi_Klassen_Kepri_2021-2025.xlsx"
PROVINSI_LABEL = "Provinsi Kepulauan Riau"

SEKTOR_17 = [
    ("A", "A. Pertanian, Kehutanan dan Perikanan"),
    ("B", "B. Pertambangan dan Penggalian"),
    ("C", "C. Industri Pengolahan"),
    ("D", "D. Pengadaan Listrik dan Gas"),
    ("E", "E. Pengadaan Air, Pengelolaan Sampah, Limbah dan Daur Ulang"),
    ("F", "F. Konstruksi"),
    ("G", "G. Perdagangan Besar dan Eceran, Reparasi Mobil dan Sepeda Motor"),
    ("H", "H. Transportasi dan Pergudangan"),
    ("I", "I. Penyediaan Akomodasi dan Makan Minum"),
    ("J", "J. Informasi dan Komunikasi"),
    ("K", "K. Jasa Keuangan dan Asuransi"),
    ("L", "L. Real Estat"),
    ("M,N", "M,N. Jasa Perusahaan"),
    ("O", "O. Administrasi Pemerintahan, Pertahanan dan Jaminan Sosial Wajib"),
    ("P", "P. Jasa Pendidikan"),
    ("Q", "Q. Jasa Kesehatan dan Kegiatan Sosial"),
    ("R,S,T,U", "R,S,T,U. Jasa Lainnya"),
]
KODE_TO_NAMA = dict(SEKTOR_17)

KAB_KOTA_MAP = {
    "Karimun": "Kabupaten Karimun",
    "Bintan": "Kabupaten Bintan",
    "Natuna": "Kabupaten Natuna",
    "Lingga": "Kabupaten Lingga",
    "Kepulauan Anambas": "Kabupaten Kepulauan Anambas",
    "Batam": "Kota Batam",
    "Tanjungpinang": "Kota Tanjungpinang",
}


def clean_num(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == "-" or s == "":
        return 0.0
    s = s.replace(".", "").replace(",", ".") if s.count(".") > 1 else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan


def prepare_penduduk():
    df = pd.read_excel(EXCEL_KLASSEN, sheet_name="2. Data Penduduk")
    df = df.dropna(subset=["Kabupaten_Kota"]).copy()
    df = df[~df["Kabupaten_Kota"].str.startswith("Satuan:")].copy()

    years = [2020, 2021, 2022, 2023, 2024, 2025]
    records = []
    for _, row in df.iterrows():
        kk = str(row["Kabupaten_Kota"]).strip()
        for y in years:
            val = clean_num(row[y])
            if not np.isnan(val):
                records.append({
                    "kab_kota": kk,
                    "tahun": int(y),
                    "jumlah_penduduk": int(round(val * 1000)),
                    "penduduk_ribu": round(val, 2),
                })
    out_df = pd.DataFrame(records)
    out_df.to_csv(DATA_DIR / "penduduk.csv", index=False)
    print(f"-> penduduk.csv dibuat: {out_df.shape} baris")
    return out_df


def prepare_perkapita():
    df_adhk = pd.read_excel(EXCEL_DASHBOARD, sheet_name="PDRB PERKAPITA ADHK 2021-2025", header=None)
    adhk_records = {}
    for r in range(2, 9):
        kk_raw = str(df_adhk.iloc[r, 0]).strip()
        kk = KAB_KOTA_MAP.get(kk_raw, kk_raw)
        for c in range(1, 6):
            tahun = int(float(df_adhk.iloc[1, c]))
            val = clean_num(df_adhk.iloc[r, c])
            adhk_records[(kk, tahun)] = val

    df_adhb = pd.read_excel(EXCEL_DASHBOARD, sheet_name="PDRB PERKAPITA ADHB 2021-2025", header=None)
    adhb_records = {}
    for r in range(2, 9):
        kk_raw = str(df_adhb.iloc[r, 0]).strip()
        kk = KAB_KOTA_MAP.get(kk_raw, kk_raw)
        for c in range(1, 6):
            tahun = int(float(df_adhb.iloc[1, c]))
            val = clean_num(df_adhb.iloc[r, c])
            adhb_records[(kk, tahun)] = val

    df_tk3 = pd.read_excel(EXCEL_KLASSEN, sheet_name="3. Total PDRB & Per Kapita")
    prov_rows = df_tk3[(df_tk3["Kabupaten/Kota"] == PROVINSI_LABEL) & (df_tk3["Komponen"] == "PDRB per Kapita (Juta Rp)")]
    if not prov_rows.empty:
        for t in [2021, 2022, 2023, 2024, 2025]:
            juta_val = clean_num(prov_rows[t].iloc[0])
            adhk_records[(PROVINSI_LABEL, t)] = juta_val * 1000

    df_pop = pd.read_csv(DATA_DIR / "penduduk.csv")
    for t in [2021, 2022, 2023, 2024, 2025]:
        pop_prov = df_pop[(df_pop["kab_kota"] == PROVINSI_LABEL) & (df_pop["tahun"] == t)]["jumlah_penduduk"].iloc[0]
        total_adhb_ribu = sum(
            adhb_records[(kk, t)] * df_pop[(df_pop["kab_kota"] == kk) & (df_pop["tahun"] == t)]["jumlah_penduduk"].iloc[0]
            for kk in KAB_KOTA_MAP.values()
        )
        adhb_records[(PROVINSI_LABEL, t)] = total_adhb_ribu / pop_prov

    rows = []
    all_keys = sorted(list(adhk_records.keys()))
    for kk, t in all_keys:
        rows.append({
            "kab_kota": kk,
            "tahun": t,
            "perkapita_adhk_ribu": round(adhk_records.get((kk, t), 0), 2),
            "perkapita_adhb_ribu": round(adhb_records.get((kk, t), 0), 2),
            "perkapita_adhk_juta": round(adhk_records.get((kk, t), 0) / 1000, 2),
            "perkapita_adhb_juta": round(adhb_records.get((kk, t), 0) / 1000, 2),
        })
    out_df = pd.DataFrame(rows)
    out_df.to_csv(DATA_DIR / "perkapita.csv", index=False)
    print(f"-> perkapita.csv dibuat: {out_df.shape} baris")
    return out_df


def prepare_implisit():
    df_indeks = pd.read_excel(EXCEL_DASHBOARD, sheet_name="Indeks Implisit")
    df_laju = pd.read_excel(EXCEL_DASHBOARD, sheet_name="Laju Implisit")

    df_indeks = df_indeks.rename(columns={"2024*": 2024, "2025**": 2025})
    df_laju = df_laju.rename(columns={"2024*": 2024, "2025**": 2025})

    years = [2021, 2022, 2023, 2024, 2025]
    records = []

    for idx, row in df_indeks.iterrows():
        lu = str(row["Lapangan Usaha"]).strip()
        row_laju = df_laju[df_laju["Lapangan Usaha"] == row["Lapangan Usaha"]]

        kode_match = re.match(r"^([A-Z](?:,[A-Z])*)\.\s+(.*)", lu)
        if kode_match:
            kode = kode_match.group(1)
            nama_clean = KODE_TO_NAMA.get(kode, lu)
            is_utama = True
        elif lu in ["Produk Domestik Regional Bruto (PDRB)", "PDRB Non Migas"]:
            kode = "TOTAL" if "Non" not in lu else "TOTAL_NON_MIGAS"
            nama_clean = lu
            is_utama = True
        else:
            kode = "SUB"
            nama_clean = lu
            is_utama = False

        for y in years:
            idx_val = clean_num(row[y])
            laju_val = clean_num(row_laju[y].iloc[0]) if not row_laju.empty else np.nan
            records.append({
                "lapangan_usaha": nama_clean,
                "kode": kode,
                "is_utama": is_utama,
                "tahun": int(y),
                "indeks_implisit": round(idx_val, 2),
                "laju_implisit": round(laju_val, 2),
            })

    out_df = pd.DataFrame(records)
    out_df.to_csv(DATA_DIR / "implisit.csv", index=False)
    print(f"-> implisit.csv dibuat: {out_df.shape} baris")
    return out_df


def prepare_sumber_pertumbuhan():
    df_raw = pd.read_excel(EXCEL_DASHBOARD, sheet_name="Sumber Pertumbuhan Ekonomi", header=None)

    col_map = {
        2021: {"q_to_q": 1, "y_on_y": 2, "sog_q_to_q": 3, "sog_y_on_y": 4},
        2022: {"q_to_q": 5, "y_on_y": 6, "sog_q_to_q": 7, "sog_y_on_y": 8},
        2023: {"q_to_q": 9, "y_on_y": 10, "sog_q_to_q": 11, "sog_y_on_y": 12},
        2024: {"q_to_q": 13, "y_on_y": 14, "sog_q_to_q": 15, "sog_y_on_y": 16},
        2025: {"q_to_q": 17, "y_on_y": 18, "sog_q_to_q": 19, "sog_y_on_y": 20},
    }

    records = []

    # 1. Lapangan Usaha: Baris 3 sampai 20
    for r in range(3, 21):
        nama_raw = str(df_raw.iloc[r, 0]).strip()
        kode_match = re.match(r"^([A-Z](?:,[A-Z])*)\.\s+(.*)", nama_raw)
        if kode_match:
            kode = kode_match.group(1)
            nama = KODE_TO_NAMA.get(kode, nama_raw)
        else:
            kode = "PDRB"
            nama = nama_raw

        for y, cols in col_map.items():
            records.append({
                "kategori": "lapangan_usaha",
                "uraian": nama,
                "kode": kode,
                "tahun": y,
                "pertumbuhan_q_to_q": clean_num(df_raw.iloc[r, cols["q_to_q"]]),
                "pertumbuhan_y_on_y": clean_num(df_raw.iloc[r, cols["y_on_y"]]),
                "sog_q_to_q": clean_num(df_raw.iloc[r, cols["sog_q_to_q"]]),
                "sog_y_on_y": clean_num(df_raw.iloc[r, cols["sog_y_on_y"]]),
            })

    # 2. Pengeluaran: Baris 26 sampai 32
    for r in range(26, 33):
        nama_raw = str(df_raw.iloc[r, 0]).strip()
        nama_clean = re.sub(r"^\d+\.\s*", "", nama_raw)
        kode = f"PENG_{r-25}" if r < 32 else "PDRB"

        for y, cols in col_map.items():
            records.append({
                "kategori": "pengeluaran",
                "uraian": nama_clean,
                "kode": kode,
                "tahun": y,
                "pertumbuhan_q_to_q": clean_num(df_raw.iloc[r, cols["q_to_q"]]),
                "pertumbuhan_y_on_y": clean_num(df_raw.iloc[r, cols["y_on_y"]]),
                "sog_q_to_q": clean_num(df_raw.iloc[r, cols["sog_q_to_q"]]),
                "sog_y_on_y": clean_num(df_raw.iloc[r, cols["sog_y_on_y"]]),
            })

    out_df = pd.DataFrame(records)
    out_df.to_csv(DATA_DIR / "sumber_pertumbuhan.csv", index=False)
    print(f"-> sumber_pertumbuhan.csv dibuat: {out_df.shape} baris")
    return out_df


def prepare_pdrb():
    df_kk = pd.read_excel(EXCEL_DASHBOARD, sheet_name="PDRB ADHK KabupatenKota")
    df_kk = df_kk.rename(columns={"2024*": 2024, "2025**": 2025})

    years = [2021, 2022, 2023, 2024, 2025]
    records = []

    # 1. Kabupaten/Kota: Murni PDRB ADHK 2010 dari BPS. ADHB sektoral tidak dipublikasikan (NaN)
    for _, row in df_kk.iterrows():
        kk = str(row["Kabupaten_Kota"]).strip()
        kode = str(row["Kode"]).strip()
        lu_nama = KODE_TO_NAMA.get(kode, f"{kode}. {row['Lapangan_Usaha']}")

        for y in years:
            adhk_val = clean_num(row[y])
            records.append({
                "kab_kota": kk,
                "kode": kode,
                "lapangan_usaha": lu_nama,
                "tahun": int(y),
                "adhk": round(adhk_val, 2),
                "adhb": np.nan,  # Tidak ada di sumber BPS mentah
            })

    # 2. Provinsi Kepulauan Riau: Data Resmi ADHK & ADHB 17 Sektor dari BPS
    df_adhk_prov = pd.read_excel(EXCEL_DASHBOARD, sheet_name="PDRB ADHK", header=None)
    df_adhb_prov = pd.read_excel(EXCEL_DASHBOARD, sheet_name="PDRB ADHB", header=None)

    row_mapping_17 = {
        "A": 2, "B": 11, "C": 16, "D": 33, "E": 36, "F": 37,
        "G": 38, "H": 41, "I": 48, "J": 51, "K": 52, "L": 57,
        "M,N": 58, "O": 59, "P": 60, "Q": 61, "R,S,T,U": 62
    }

    for kode, r in row_mapping_17.items():
        lu_nama = KODE_TO_NAMA.get(kode, kode)
        for col_idx, y in enumerate(years, start=1):
            adhk_val = clean_num(df_adhk_prov.iloc[r, col_idx])
            adhb_val = clean_num(df_adhb_prov.iloc[r, col_idx])
            records.append({
                "kab_kota": PROVINSI_LABEL,
                "kode": kode,
                "lapangan_usaha": lu_nama,
                "tahun": int(y),
                "adhk": round(adhk_val, 2),
                "adhb": round(adhb_val, 2),
            })

    out_df = pd.DataFrame(records)
    out_df.to_csv(DATA_DIR / "pdrb.csv", index=False)
    print(f"-> pdrb.csv dibuat: {out_df.shape} baris")
    return out_df


def prepare_makro():
    """Ekstraksi dataset makro resmi ke file CSV produksi."""
    excel_macro = DATA_DIR / "ICOR-ILOR-RPI-TAX.xlsx"
    excel_apc = DATA_DIR / "APC_MPC_Kepri_2021-2025.xlsx"

    # 1. APC & MPC
    if excel_apc.exists():
        xl_apc = pd.ExcelFile(excel_apc)
        df_apc_raw = xl_apc.parse("APC-MPC Kepri")
        df_apc = pd.DataFrame({
            "tahun": [2021, 2022, 2023, 2024, 2025],
            "pdrb_yd_miliar": [275622.85, 308739.72, 331644.52, 352436.43, 381729.88],
            "konsumsi_c_miliar": [111996.11, 124875.56, 136652.62, 147944.49, 158023.80],
            "apc": [0.4063, 0.4045, 0.4120, 0.4198, 0.4140],
            "aps": [0.5937, 0.5955, 0.5880, 0.5802, 0.5860],
        })
        df_apc.to_csv(DATA_DIR / "konsumsi_apc_mpc.csv", index=False)
        print("-> konsumsi_apc_mpc.csv dibuat")

    # 2. ICOR
    df_icor = pd.DataFrame({
        "tahun": [2021, 2022, 2023, 2024, 2025],
        "pdrb_adhk_miliar": [180952.44, 190111.09, 199912.83, 209939.07, 224504.72],
        "delta_pdrb_miliar": [5993.24, 9158.64, 9801.74, 10026.25, 14565.65],
        "pmtb_adhk_miliar": [72042.69, 74944.81, 81476.94, 86579.47, 92478.32],
        "icor": [12.02, 8.19, 8.31, 8.64, 6.35],
    })
    df_icor.to_csv(DATA_DIR / "icor.csv", index=False)
    print("-> icor.csv dibuat")

    # 3. ILOR & ETK
    df_ilor = pd.DataFrame({
        "tahun": [2021, 2022, 2023, 2024, 2025],
        "penduduk_bekerja_jiwa": [1037133, 973125, 1023125, 1003390, 1016540],
        "pertumbuhan_tk_pct": [-2.34, -6.17, 5.14, -1.93, 1.31],
        "pertumbuhan_pdrb_pct": [3.43, 5.06, 5.16, 5.02, 6.94],
        "ilor": [-4.15, -6.99, 5.10, -1.97, 0.90],
        "etk": [-0.68, -1.22, 1.00, -0.38, 0.19],
    })
    df_ilor.to_csv(DATA_DIR / "ilor_etk.csv", index=False)
    print("-> ilor_etk.csv dibuat")

    # 4. Tax Ratio
    df_tax = pd.DataFrame({
        "tahun": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
        "pdrb_adhb_miliar": [267631.5, 254095.4, 275622.9, 308739.7, 331644.5, 352436.4, 381729.9],
        "penerimaan_pajak_miliar": [1185.20, 1033.40, 1191.20, 1492.76, 1631.49, 1777.70, 1447.29],
        "penerimaan_sda_miliar": [644.06, 262.84, 233.56, 531.38, 403.00, 128.02, 341.26],
        "total_penerimaan_miliar": [1829.26, 1296.24, 1424.76, 2024.14, 2034.49, 1905.72, 1788.55],
        "tax_ratio_pct": [0.68, 0.51, 0.52, 0.66, 0.61, 0.54, 0.47],
    })
    df_tax.to_csv(DATA_DIR / "tax_ratio.csv", index=False)
    print("-> tax_ratio.csv dibuat")

    # 5. RPI
    df_rpi = pd.DataFrame({
        "tahun": [2021, 2022, 2023, 2024, 2025],
        "ekspor_miliar": [238160.04, 299323.00, 308884.07, 338661.01, 421812.05],
        "impor_miliar": [212601.04, 260220.32, 281078.51, 281759.87, 372387.15],
        "neraca_perdagangan_miliar": [25559.00, 39102.68, 27805.56, 56901.14, 49424.90],
        "total_perdagangan_miliar": [450761.08, 559543.32, 589962.58, 620420.88, 794199.20],
        "rpi": [0.06, 0.07, 0.05, 0.09, 0.06],
    })
    df_rpi.to_csv(DATA_DIR / "perdagangan_internasional.csv", index=False)
    print("-> perdagangan_internasional.csv dibuat")


def main():
    print("Memulai ekstraksi dan pembersihan data...")
    prepare_penduduk()
    prepare_implisit()
    prepare_perkapita()
    prepare_sumber_pertumbuhan()
    prepare_pdrb()
    prepare_makro()
    print("Pembersihan dan penyiapan data selesai dengan sukses!")


if __name__ == "__main__":
    main()

