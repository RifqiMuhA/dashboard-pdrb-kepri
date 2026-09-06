"""
Kumpulan fungsi perhitungan analisis PDRB, mengikuti rumus pada materi
"Analisis PDB/PDRB". Semua fungsi menerima/mengembalikan pandas DataFrame
long-format supaya gampang disambungkan ke Plotly Express di pages/.
"""

import pandas as pd
from theme import CATEGORY_PALETTE


# ---------------------------------------------------------------------------
# Util kecil
# ---------------------------------------------------------------------------
def get_category_color_map(categories: list) -> dict:
    """Mapping warna tetap per kategori agar konsisten di semua chart."""
    cats = sorted(categories)
    return {cat: CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i, cat in enumerate(cats)}


# ---------------------------------------------------------------------------
# 1. MONITORING PERILAKU EKONOMI
# ---------------------------------------------------------------------------
def hitung_laju_pertumbuhan(df_pdrb: pd.DataFrame, value_col: str = "adhk") -> pd.DataFrame:
    """r = (Yt - Yt-1) / Yt-1 x 100%, per kab_kota (total semua lapangan usaha)."""
    total = df_pdrb.groupby(["kab_kota", "tahun"], as_index=False)[value_col].sum()
    total = total.sort_values(["kab_kota", "tahun"])
    total["laju_pertumbuhan"] = total.groupby("kab_kota")[value_col].pct_change() * 100
    return total


def hitung_kontribusi(df_pdrb: pd.DataFrame, kab_kota: str, tahun: int) -> pd.DataFrame:
    """Proporsi tiap lapangan usaha terhadap total PDRB ADHB, wilayah & tahun tertentu."""
    sub = df_pdrb[(df_pdrb["kab_kota"] == kab_kota) & (df_pdrb["tahun"] == tahun)].copy()
    total = sub["adhb"].sum()
    sub["kontribusi_persen"] = sub["adhb"] / total * 100
    return sub[["lapangan_usaha", "adhb", "kontribusi_persen"]].sort_values(
        "kontribusi_persen", ascending=False
    )


def hitung_pdrb_perkapita(df_pdrb: pd.DataFrame, df_penduduk: pd.DataFrame) -> pd.DataFrame:
    """PDRB perkapita = total PDRB ADHB / jumlah penduduk (unit: sama dgn adhb / jiwa)."""
    total_pdrb = df_pdrb.groupby(["kab_kota", "tahun"], as_index=False)["adhb"].sum()
    merged = total_pdrb.merge(df_penduduk, on=["kab_kota", "tahun"], how="inner")
    merged["pdrb_perkapita"] = merged["adhb"] / merged["jumlah_penduduk"]
    return merged


def hitung_sumber_pertumbuhan(df_pdrb: pd.DataFrame, kab_kota: str) -> pd.DataFrame:
    """SOG_it = (y_it - y_it-1) / sum(y_it-1) x 100%, per lapangan usaha."""
    sub = df_pdrb[df_pdrb["kab_kota"] == kab_kota].copy().sort_values(["lapangan_usaha", "tahun"])
    sub["adhk_prev"] = sub.groupby("lapangan_usaha")["adhk"].shift(1)
    total_prev = sub.groupby("tahun")["adhk_prev"].transform("sum")
    sub["sog"] = (sub["adhk"] - sub["adhk_prev"]) / total_prev * 100
    return sub.dropna(subset=["sog"])[["lapangan_usaha", "tahun", "sog"]]


def hitung_indeks_implisit(df_pdrb: pd.DataFrame, kab_kota: str) -> pd.DataFrame:
    """I_t = (ADHB / ADHK) x 100. Total seluruh lapangan usaha per tahun."""
    sub = df_pdrb[df_pdrb["kab_kota"] == kab_kota].groupby("tahun", as_index=False)[
        ["adhb", "adhk"]
    ].sum()
    sub = sub.sort_values("tahun")
    sub["indeks_implisit"] = sub["adhb"] / sub["adhk"] * 100
    sub["laju_indeks_implisit"] = sub["indeks_implisit"].pct_change() * 100
    return sub


# ---------------------------------------------------------------------------
# 2. ANALISIS ANTAR WILAYAH
# ---------------------------------------------------------------------------
def hitung_williamson(df_perkapita: pd.DataFrame, df_penduduk: pd.DataFrame, tahun: int) -> float:
    """
    Iw = sqrt( sum( (Yi - Yn)^2 * (Pi/Pn) ) ) / Yn
    Yi = PDRB perkapita kab/kota i, Yn = PDRB perkapita rata-rata (provinsi),
    Pi = penduduk kab/kota i, Pn = total penduduk semua kab/kota.
    """
    sub = df_perkapita[df_perkapita["tahun"] == tahun].copy()
    sub = sub.merge(df_penduduk, on=["kab_kota", "tahun"], suffixes=("", "_pop"))
    total_pop = sub["jumlah_penduduk"].sum()
    yn = (sub["pdrb_perkapita"] * sub["jumlah_penduduk"]).sum() / total_pop  # rata-rata tertimbang
    sub["weight"] = sub["jumlah_penduduk"] / total_pop
    sub["sq_dev"] = (sub["pdrb_perkapita"] - yn) ** 2 * sub["weight"]
    iw = (sub["sq_dev"].sum()) ** 0.5 / yn
    return iw


def hitung_williamson_series(df_perkapita: pd.DataFrame, df_penduduk: pd.DataFrame) -> pd.DataFrame:
    tahun_list = sorted(df_perkapita["tahun"].unique())
    rows = [{"tahun": t, "indeks_williamson": hitung_williamson(df_perkapita, df_penduduk, t)} for t in tahun_list]
    return pd.DataFrame(rows)


def hitung_bonet(df_perkapita: pd.DataFrame, tahun: int, provinsi_label: str) -> pd.DataFrame:
    """IB_i = | PDRBperkapita_i / PDRBperkapita_reference - 1 |"""
    sub = df_perkapita[df_perkapita["tahun"] == tahun].copy()
    ref_row = sub[sub["kab_kota"] == provinsi_label]
    if ref_row.empty:
        raise ValueError(f"Data referensi provinsi '{provinsi_label}' tidak ditemukan pada tahun {tahun}")
    ref_val = ref_row["pdrb_perkapita"].iloc[0]
    sub = sub[sub["kab_kota"] != provinsi_label]
    sub["indeks_bonet"] = (sub["pdrb_perkapita"] / ref_val - 1).abs()
    return sub[["kab_kota", "pdrb_perkapita", "indeks_bonet"]].sort_values("indeks_bonet", ascending=False)


def hitung_shift_share(
    df_pdrb: pd.DataFrame, kab_kota: str, provinsi_label: str, tahun_awal: int, tahun_akhir: int
) -> pd.DataFrame:
    """
    SS = Regional Share + Proportional Shift + Differential Shift
    (formulasi Sjafrizal, 2008) per lapangan usaha.
    """
    def get_val(df, wilayah, lu, tahun, col="adhk"):
        row = df[(df["kab_kota"] == wilayah) & (df["lapangan_usaha"] == lu) & (df["tahun"] == tahun)]
        return row[col].iloc[0] if not row.empty else None

    lu_list = sorted(df_pdrb["lapangan_usaha"].unique())
    Y0 = df_pdrb[(df_pdrb["kab_kota"] == provinsi_label) & (df_pdrb["tahun"] == tahun_awal)]["adhk"].sum()
    Yt = df_pdrb[(df_pdrb["kab_kota"] == provinsi_label) & (df_pdrb["tahun"] == tahun_akhir)]["adhk"].sum()

    rows = []
    for lu in lu_list:
        y0 = get_val(df_pdrb, kab_kota, lu, tahun_awal)
        yt = get_val(df_pdrb, kab_kota, lu, tahun_akhir)
        Yi0 = get_val(df_pdrb, provinsi_label, lu, tahun_awal)
        Yit = get_val(df_pdrb, provinsi_label, lu, tahun_akhir)
        if None in (y0, yt, Yi0, Yit) or y0 == 0 or Yi0 == 0 or Y0 == 0:
            continue
        regional_share = y0 * (Yt / Y0 - 1)
        proportional_shift = y0 * (Yit / Yi0 - Yt / Y0)
        differential_shift = y0 * (yt / y0 - Yit / Yi0)
        rows.append(
            {
                "lapangan_usaha": lu,
                "regional_share": regional_share,
                "proportional_shift": proportional_shift,
                "differential_shift": differential_shift,
                "total_shift_share": regional_share + proportional_shift + differential_shift,
            }
        )
    return pd.DataFrame(rows)


def hitung_lq(df_pdrb: pd.DataFrame, kab_kota: str, provinsi_label: str, tahun: int, value_col: str = "adhk") -> pd.DataFrame:
    """LQ = (vi/vt) / (Vi/Vt): vi=sektor i wilayah, vt=total wilayah, Vi=sektor i acuan, Vt=total acuan."""
    sub_wilayah = df_pdrb[(df_pdrb["kab_kota"] == kab_kota) & (df_pdrb["tahun"] == tahun)]
    sub_acuan = df_pdrb[(df_pdrb["kab_kota"] == provinsi_label) & (df_pdrb["tahun"] == tahun)]

    vt = sub_wilayah[value_col].sum()
    Vt = sub_acuan[value_col].sum()

    merged = sub_wilayah[["lapangan_usaha", value_col]].merge(
        sub_acuan[["lapangan_usaha", value_col]], on="lapangan_usaha", suffixes=("_wilayah", "_acuan")
    )
    merged["lq"] = (merged[f"{value_col}_wilayah"] / vt) / (merged[f"{value_col}_acuan"] / Vt)
    merged["status"] = merged["lq"].apply(lambda x: "Basis" if x > 1 else "Non Basis")
    return merged[["lapangan_usaha", "lq", "status"]]


def hitung_lq_matrix(df_pdrb: pd.DataFrame, provinsi_label: str, tahun: int, value_col: str = "adhk") -> pd.DataFrame:
    """LQ semua kab/kota x semua lapangan usaha untuk satu tahun -> untuk heatmap."""
    kk_list = sorted(df_pdrb.loc[df_pdrb["kab_kota"] != provinsi_label, "kab_kota"].unique())
    results = []
    for kk in kk_list:
        lq_df = hitung_lq(df_pdrb, kk, provinsi_label, tahun, value_col)
        lq_df["kab_kota"] = kk
        results.append(lq_df)
    return pd.concat(results, ignore_index=True)


def hitung_tipologi_klassen(
    df_pdrb: pd.DataFrame, df_penduduk: pd.DataFrame, provinsi_label: str, tahun_awal: int, tahun_akhir: int
) -> pd.DataFrame:
    """
    Kuadran I  : pertumbuhan > acuan & perkapita > acuan (maju & tumbuh cepat)
    Kuadran II : pertumbuhan > acuan & perkapita < acuan (sedang berkembang)
    Kuadran III: pertumbuhan < acuan & perkapita > acuan (maju tapi tertekan)
    Kuadran IV : pertumbuhan < acuan & perkapita < acuan (relatif tertinggal)
    """
    df_perkapita = hitung_pdrb_perkapita(df_pdrb, df_penduduk)
    df_growth = hitung_laju_pertumbuhan(df_pdrb, value_col="adhk")

    perkapita_avg = (
        df_perkapita[(df_perkapita["tahun"] >= tahun_awal) & (df_perkapita["tahun"] <= tahun_akhir)]
        .groupby("kab_kota", as_index=False)["pdrb_perkapita"].mean()
    )
    growth_avg = (
        df_growth[(df_growth["tahun"] >= tahun_awal) & (df_growth["tahun"] <= tahun_akhir)]
        .groupby("kab_kota", as_index=False)["laju_pertumbuhan"].mean()
    )

    merged = perkapita_avg.merge(growth_avg, on="kab_kota")

    ref_perkapita = merged.loc[merged["kab_kota"] == provinsi_label, "pdrb_perkapita"]
    ref_growth = merged.loc[merged["kab_kota"] == provinsi_label, "laju_pertumbuhan"]
    ref_perkapita = ref_perkapita.iloc[0] if not ref_perkapita.empty else merged["pdrb_perkapita"].mean()
    ref_growth = ref_growth.iloc[0] if not ref_growth.empty else merged["laju_pertumbuhan"].mean()

    merged = merged[merged["kab_kota"] != provinsi_label].copy()

    def klasifikasi(row):
        if row["laju_pertumbuhan"] >= ref_growth and row["pdrb_perkapita"] >= ref_perkapita:
            return "I - Maju & Tumbuh Cepat"
        elif row["laju_pertumbuhan"] >= ref_growth and row["pdrb_perkapita"] < ref_perkapita:
            return "II - Sedang Berkembang"
        elif row["laju_pertumbuhan"] < ref_growth and row["pdrb_perkapita"] >= ref_perkapita:
            return "III - Maju Tapi Tertekan"
        else:
            return "IV - Relatif Tertinggal"

    merged["kuadran"] = merged.apply(klasifikasi, axis=1)
    merged.attrs["ref_perkapita"] = ref_perkapita
    merged.attrs["ref_growth"] = ref_growth
    return merged


# ---------------------------------------------------------------------------
# 3. ANALISIS MAKRO EKONOMI (level provinsi)
# ---------------------------------------------------------------------------
def hitung_apc_aps(df_pengeluaran: pd.DataFrame) -> pd.DataFrame:
    """APC = Konsumsi Akhir / Yd ; APS = Tabungan / Yd. Yd diproksi dari total ADHB."""
    pivot = df_pengeluaran.pivot(index="tahun", columns="uraian", values="adhb")
    konsumsi_akhir = pivot[["Konsumsi Rumah Tangga", "Konsumsi LNPRT", "Konsumsi Pemerintah"]].sum(axis=1)
    # Proksi pendapatan disposabel = konsumsi akhir + PMTB (mendekati definisi Yd jika tabungan = investasi domestik)
    yd_proxy = konsumsi_akhir + pivot["PMTB"]
    apc = konsumsi_akhir / yd_proxy
    aps = 1 - apc
    result = pd.DataFrame({"tahun": pivot.index, "apc": apc.values, "aps": aps.values})
    return result


def hitung_rpi(df_pengeluaran: pd.DataFrame) -> pd.DataFrame:
    """RPI = (X - M) / (X + M)"""
    pivot = df_pengeluaran.pivot(index="tahun", columns="uraian", values="adhb")
    X = pivot["Ekspor"]
    M = pivot["Impor"]
    rpi = (X - M) / (X + M)
    return pd.DataFrame({"tahun": pivot.index, "rpi": rpi.values})


def hitung_icor(df_pdrb: pd.DataFrame, df_pengeluaran: pd.DataFrame, provinsi_label: str) -> pd.DataFrame:
    """ICOR = delta_PMTB / delta_PDRB(ADHK), dari tahun sebelumnya ke tahun berjalan."""
    pdrb_prov = (
        df_pdrb[df_pdrb["kab_kota"] == provinsi_label]
        .groupby("tahun", as_index=False)["adhk"].sum()
        .sort_values("tahun")
    )
    pmtb = df_pengeluaran[df_pengeluaran["uraian"] == "PMTB"][["tahun", "adhk"]].sort_values("tahun")
    merged = pdrb_prov.merge(pmtb, on="tahun", suffixes=("_pdrb", "_pmtb"))
    merged["delta_pdrb"] = merged["adhk_pdrb"].diff()
    merged["icor"] = merged["adhk_pmtb"] / merged["delta_pdrb"]
    return merged.dropna(subset=["icor"])[["tahun", "icor"]]


def hitung_ilor_elastisitas(df_tenaga_kerja: pd.DataFrame, df_pdrb: pd.DataFrame, provinsi_label: str) -> pd.DataFrame:
    """
    ILOR = delta_TK / delta_Y ; E_TK = (%delta_TK) / (%delta_Y), per lapangan usaha,
    dihitung antar dua tahun terjauh yang tersedia (awal vs akhir).
    """
    tahun_awal = df_tenaga_kerja["tahun"].min()
    tahun_akhir = df_tenaga_kerja["tahun"].max()

    tk = df_tenaga_kerja.pivot(index="lapangan_usaha", columns="tahun", values="jumlah_tenaga_kerja")
    pdrb_prov = df_pdrb[df_pdrb["kab_kota"] == provinsi_label]
    y = pdrb_prov.pivot(index="lapangan_usaha", columns="tahun", values="adhk")

    delta_tk = tk[tahun_akhir] - tk[tahun_awal]
    delta_y = y[tahun_akhir] - y[tahun_awal]

    ilor = delta_tk / delta_y
    elastisitas = (delta_tk / tk[tahun_awal]) / (delta_y / y[tahun_awal])

    result = pd.DataFrame({"ilor": ilor, "elastisitas_tk": elastisitas}).reset_index()
    return result


def hitung_tax_ratio(df_pajak: pd.DataFrame, df_pdrb: pd.DataFrame, provinsi_label: str) -> pd.DataFrame:
    """Tax Ratio = (Pajak + SDA) / PDRB ADHB x 100%"""
    pdrb_prov = (
        df_pdrb[df_pdrb["kab_kota"] == provinsi_label]
        .groupby("tahun", as_index=False)["adhb"].sum()
    )
    merged = df_pajak.merge(pdrb_prov, on="tahun")
    merged["tax_ratio"] = (merged["penerimaan_pajak"] + merged["penerimaan_sda"]) / merged["adhb"] * 100
    return merged[["tahun", "tax_ratio"]]
