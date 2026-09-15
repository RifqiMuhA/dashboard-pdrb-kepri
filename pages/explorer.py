import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
import pandas as pd

from utils.data_loader import DATA
from utils.components import page_heading
from theme import COLORS

dash.register_page(__name__, path="/explorer", name="Data Explorer")

# ─────────────────────────────────────────────────────────────────────────────
# Definisi Metadata & Opsi Dataset Lengkap (100% Data Riil Terverifikasi)
# ─────────────────────────────────────────────────────────────────────────────
DATASET_METADATA = {
    "pdrb": {
        "title": "PDRB Menurut Lapangan Usaha (17 Sektor)",
        "category": "PDRB & Sektoral Regional",
        "source": "BPS Provinsi Kepulauan Riau (Publikasi PDRB Menurut Lapangan Usaha 2021–2025)",
        "period": "2021 – 2025",
        "units": "Miliar Rupiah (ADHK 2010 & ADHB)",
        "scope": "7 Kabupaten/Kota & Provinsi Kepulauan Riau",
        "desc": (
            "Memuat volume Produk Domestik Regional Bruto (PDRB) riil atas dasar harga konstan 2010 (ADHK) "
            "dan harga berlaku (ADHB) untuk 17 kategori lapangan usaha. "
            "Catatan: Pada tingkat kabupaten/kota, publikasi berkala resmi BPS mencakup rincian sektoral ADHK."
        ),
        "column_labels": {
            "kab_kota": "Kabupaten / Kota",
            "kode": "Kode Kategori",
            "lapangan_usaha": "Lapangan Usaha (17 Sektor)",
            "tahun": "Tahun",
            "adhk": "ADHK 2010 (Miliar Rp)",
            "adhb": "ADHB (Miliar Rp)",
        },
    },
    "perkapita": {
        "title": "PDRB Per Kapita (Riil & Nominal)",
        "category": "Disparitas & Kesejahteraan Wilayah",
        "source": "BPS Provinsi Kepulauan Riau (Publikasi Indikator Makro & Perkapita 2021–2025)",
        "period": "2021 – 2025",
        "units": "Juta Rupiah / Jiwa & Ribu Rupiah / Jiwa",
        "scope": "7 Kabupaten/Kota & Provinsi Kepulauan Riau",
        "desc": (
            "Ukuran rata-rata nilai tambah bruto ekonomi yang dihasilkan per jiwa penduduk, mencakup basis "
            "harga konstan 2010 (ADHK) dan harga berlaku (ADHB) dalam satuan Ribu Rupiah dan Juta Rupiah."
        ),
        "column_labels": {
            "kab_kota": "Kabupaten / Kota",
            "tahun": "Tahun",
            "perkapita_adhk_ribu": "ADHK (Ribu Rp/jiwa)",
            "perkapita_adhb_ribu": "ADHB (Ribu Rp/jiwa)",
            "perkapita_adhk_juta": "ADHK (Juta Rp/jiwa)",
            "perkapita_adhb_juta": "ADHB (Juta Rp/jiwa)",
        },
    },
    "sumber_pertumbuhan": {
        "title": "Sumber Pertumbuhan Ekonomi (SOG) & Laju Pertumbuhan",
        "category": "Dekomposisi Pertumbuhan",
        "source": "BPS Provinsi Kepulauan Riau",
        "period": "2021 – 2025",
        "units": "Persen (%) & Poin Persen (SOG)",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Dekomposisi laju pertumbuhan ekonomi riil menjadi kontribusi per sektor lapangan usaha "
            "dan komponen pengeluaran, baik secara tahunan (y-on-y) maupun triwulanan (q-to-q)."
        ),
        "column_labels": {
            "kategori": "Kategori Dimensi",
            "uraian": "Uraian Lapangan Usaha / Pengeluaran",
            "kode": "Kode",
            "tahun": "Tahun",
            "pertumbuhan_q_to_q": "Laju q-to-q (%)",
            "pertumbuhan_y_on_y": "Laju y-on-y (%)",
            "sog_q_to_q": "SOG q-to-q (Poin %)",
            "sog_y_on_y": "SOG y-on-y (Poin %)",
        },
    },
    "implisit": {
        "title": "Indeks Implisit & Laju Inflasi Deflator Sektoral",
        "category": "Indeks Harga & Deflator PDRB",
        "source": "BPS Provinsi Kepulauan Riau",
        "period": "2021 – 2025",
        "units": "Indeks (2010=100) & Laju Inflasi (%)",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Indeks implisit (deflator PDRB) mengukur eskalasi harga produsen di setiap lapangan usaha "
            "serta laju perubahan harga sektoral tahunan."
        ),
        "column_labels": {
            "lapangan_usaha": "Lapangan Usaha",
            "kode": "Kode Kategori",
            "is_utama": "Sektor Utama?",
            "tahun": "Tahun",
            "indeks_implisit": "Indeks Deflator (2010=100)",
            "laju_implisit": "Laju Inflasi Implisit (%)",
        },
    },
    "penduduk": {
        "title": "Proyeksi Jumlah Penduduk Pertengahan Tahun",
        "category": "Demografi & Kependudukan",
        "source": "BPS Provinsi Kepulauan Riau (Proyeksi Penduduk)",
        "period": "2020 – 2025",
        "units": "Jiwa & Ribu Jiwa",
        "scope": "7 Kabupaten/Kota & Provinsi Kepulauan Riau",
        "desc": (
            "Data jumlah penduduk pertengahan tahun yang digunakan sebagai pembagi dalam perhitungan PDRB per kapita "
            "dan pembobot analisis ketimpangan wilayah (Williamson Index)."
        ),
        "column_labels": {
            "kab_kota": "Kabupaten / Kota",
            "tahun": "Tahun",
            "jumlah_penduduk": "Jumlah Penduduk (Jiwa)",
            "penduduk_ribu": "Jumlah Penduduk (Ribu Jiwa)",
        },
    },
    "konsumsi_apc_mpc": {
        "title": "Analisis Konsumsi Rumah Tangga (APC & MPC)",
        "category": "Makroekonomi & Konsumsi",
        "source": "BPS Provinsi Kepulauan Riau, diolah",
        "period": "2021 – 2025",
        "units": "Miliar Rp & Koefisien Proporsi (0 – 1)",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Tingkat Average Propensity to Consume (APC), Average Propensity to Save (APS), "
            "serta estimasi Marginal Propensity to Consume (MPC) fungsi Keynesian Kepulauan Riau."
        ),
        "column_labels": {
            "tahun": "Tahun",
            "pdrb_yd_miliar": "PDRB / Pendapatan Disposabel Yd (Miliar Rp)",
            "konsumsi_c_miliar": "Konsumsi Rumah Tangga C (Miliar Rp)",
            "apc": "APC (Rasio C / Yd)",
            "aps": "APS (Rasio Tabungan S / Yd)",
        },
    },
    "icor": {
        "title": "Incremental Capital Output Ratio (ICOR) & PMTB",
        "category": "Makroekonomi & Efisiensi Modal",
        "source": "BPS Provinsi Kepulauan Riau, diolah",
        "period": "2021 – 2025",
        "units": "Miliar Rupiah & Rasio Koefisien",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Indikator efisiensi investasi modal fisik di mana rasio PMTB riil terhadap tambahan output riil (Delta PDRB) "
            "menunjukkan berapa banyak investasi yang dibutuhkan untuk menghasilkan 1 unit tambahan output ekonomi."
        ),
        "column_labels": {
            "tahun": "Tahun",
            "pdrb_adhk_miliar": "PDRB Riil ADHK (Miliar Rp)",
            "delta_pdrb_miliar": "Delta Tambahan PDRB (Miliar Rp)",
            "pmtb_adhk_miliar": "PMTB Riil ADHK (Miliar Rp)",
            "icor": "Nilai Rasio ICOR",
        },
    },
    "ilor_etk": {
        "title": "Incremental Labor Output Ratio (ILOR) & Elastisitas Naker",
        "category": "Makroekonomi & Ketenagakerjaan",
        "source": "BPS Provinsi Kepulauan Riau (Sakernas & PDRB), diolah",
        "period": "2021 – 2025",
        "units": "Jiwa, Persen (%), dan Koefisien",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Mengukur responsivitas penyerapan tenaga kerja terhadap setiap persen pertumbuhan ekonomi riil Kepulauan Riau."
        ),
        "column_labels": {
            "tahun": "Tahun",
            "penduduk_bekerja_jiwa": "Penduduk Bekerja (Jiwa)",
            "pertumbuhan_tk_pct": "Pertumbuhan Naker (%)",
            "pertumbuhan_pdrb_pct": "Pertumbuhan PDRB (%)",
            "ilor": "Nilai ILOR",
            "etk": "Elastisitas Tenaga Kerja (ETK)",
        },
    },
    "tax_ratio": {
        "title": "Kinerja Penerimaan Pajak & Tax Ratio Daerah",
        "category": "Makroekonomi & Fiskal Daerah",
        "source": "DJPK Kemenkeu & BPS Prov. Kepri",
        "period": "2019 – 2025",
        "units": "Miliar Rupiah & Persen (%)",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Proporsi penerimaan perpajakan daerah dan bagi hasil SDA terhadap PDRB nominal (ADHB), "
            "merefleksikan kapasitas ruang fiskal mandiri daerah."
        ),
        "column_labels": {
            "tahun": "Tahun",
            "pdrb_adhb_miliar": "PDRB Nominal ADHB (Miliar Rp)",
            "penerimaan_pajak_miliar": "Pajak Daerah (Miliar Rp)",
            "penerimaan_sda_miliar": "Bagi Hasil SDA (Miliar Rp)",
            "total_penerimaan_miliar": "Total Penerimaan (Miliar Rp)",
            "tax_ratio_pct": "Tax Ratio (%)",
        },
    },
    "perdagangan_internasional": {
        "title": "Rasio Perdagangan Internasional (Ekspor, Impor, & RPI)",
        "category": "Makroekonomi & Perdagangan Luar Negeri",
        "source": "BPS Provinsi Kepulauan Riau, diolah",
        "period": "2021 – 2025",
        "units": "Miliar Rupiah & Rasio (-1 s.d. +1)",
        "scope": "Provinsi Kepulauan Riau",
        "desc": (
            "Memantau derajat keterbukaan perdagangan luar negeri Kepri serta surplus neraca perdagangan "
            "ekspor barang dan jasa luar negeri terhadap impor."
        ),
        "column_labels": {
            "tahun": "Tahun",
            "ekspor_miliar": "Ekspor LN ADHB (Miliar Rp)",
            "impor_miliar": "Impor LN ADHB (Miliar Rp)",
            "neraca_perdagangan_miliar": "Net Ekspor (X - M) (Miliar Rp)",
            "total_perdagangan_miliar": "Total Perdagangan (X + M) (Miliar Rp)",
            "rpi": "Rasio Perdagangan (RPI)",
        },
    },
}

DATASET_OPTIONS = [
    {"label": "1. PDRB 17 Sektor (ADHK & ADHB) — 7 Kab/Kota & Kepri", "value": "pdrb"},
    {"label": "2. PDRB Per Kapita Riil & Nominal (2021–2025)", "value": "perkapita"},
    {"label": "3. Sumber Pertumbuhan Ekonomi (SOG y-on-y & q-to-q)", "value": "sumber_pertumbuhan"},
    {"label": "4. Indeks & Laju Deflator Implisit Sektoral", "value": "implisit"},
    {"label": "5. Proyeksi Jumlah Penduduk Daerah (2020–2025)", "value": "penduduk"},
    {"label": "6. Makro: Konsumsi Rumah Tangga (APC & MPC)", "value": "konsumsi_apc_mpc"},
    {"label": "7. Makro: ICOR & Investasi Modal (PMTB)", "value": "icor"},
    {"label": "8. Makro: ILOR & Elastisitas Tenaga Kerja (ETK)", "value": "ilor_etk"},
    {"label": "9. Makro: Tax Ratio & Penerimaan Daerah", "value": "tax_ratio"},
    {"label": "10. Makro: Neraca Perdagangan & RPI (Ekspor-Impor)", "value": "perdagangan_internasional"},
]


# ─────────────────────────────────────────────────────────────────────────────
# Layout Halaman Data Explorer
# ─────────────────────────────────────────────────────────────────────────────
layout = html.Div(
    [
        page_heading(
            "Data Explorer & Repositori Resmi",
            "Eksplorasi, audit, dan unduh dataset resmi BPS & instansi terkait yang mendasari seluruh kalkulasi dashboard.",
        ),

        # ── 1. Baris Pemilihan Dataset & Tombol Download ──────────────────────
        html.Div(
            className="filter-row",
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end", "flexWrap": "wrap", "gap": "16px"},
            children=[
                html.Div(
                    className="filter-item",
                    style={"minWidth": "380px", "flex": "1"},
                    children=[
                        html.Label("Pilih Dataset Terverifikasi", className="filter-label"),
                        dcc.Dropdown(
                            id="explorer-dataset",
                            options=DATASET_OPTIONS,
                            value="pdrb",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Button(
                            [
                                html.Span("📥 ", style={"marginRight": "6px"}),
                                "Unduh Dataset (CSV)",
                            ],
                            id="btn-download-csv",
                            className="hero-button",
                            style={"height": "38px", "padding": "0 20px", "display": "inline-flex", "alignItems": "center"},
                        ),
                        dcc.Download(id="download-dataframe-csv"),
                    ]
                ),
            ],
        ),

        # ── 2. Kartu Metadata & Spesifikasi Dataset ───────────────────────────
        html.Div(id="explorer-metadata-card", style={"marginBottom": "20px"}),

        # ── 3. Tabel Data Interaktif ──────────────────────────────────────────
        html.Div(
            className="card-box",
            children=[
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "14px"},
                    children=[
                        html.H3("Pratinjau Data Bersih (Cleaned Dataset)", className="card-title", style={"margin": 0}),
                        html.Span(
                            id="explorer-row-count-badge",
                            style={
                                "fontSize": "11.5px",
                                "fontWeight": "600",
                                "color": COLORS["primary"],
                                "backgroundColor": "rgba(23, 58, 102, 0.08)",
                                "padding": "4px 12px",
                                "borderRadius": "6px",
                            },
                        ),
                    ],
                ),
                html.Div(id="explorer-table-container"),
            ],
        ),
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────────────────────────────────────
@callback(
    Output("explorer-metadata-card", "children"),
    Output("explorer-row-count-badge", "children"),
    Output("explorer-table-container", "children"),
    Input("explorer-dataset", "value"),
)
def update_explorer_view(dataset_key):
    meta = DATASET_METADATA.get(dataset_key, {})
    df_raw = DATA.get(dataset_key, pd.DataFrame())

    if df_raw.empty:
        empty_box = html.Div(
            "Dataset belum tersedia atau sedang dalam pemutakhiran.",
            style={"padding": "30px", "textAlign": "center", "color": COLORS["gray_mid"]},
        )
        return html.Div(), "0 baris data", empty_box

    # 1. Siapkan Kartu Metadata
    meta_card = html.Div(
        className="card-box",
        style={"borderLeft": f"4px solid {COLORS['accent']}", "padding": "20px 24px"},
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "flexWrap": "wrap", "gap": "10px"},
                children=[
                    html.Div([
                        html.Span(
                            meta.get("category", "Dataset").upper(),
                            style={
                                "fontSize": "10.5px",
                                "fontWeight": "700",
                                "letterSpacing": "0.8px",
                                "color": COLORS["accent_dark"],
                                "backgroundColor": "rgba(242, 183, 5, 0.12)",
                                "padding": "3px 8px",
                                "borderRadius": "4px",
                            },
                        ),
                        html.H3(meta.get("title", dataset_key), style={"fontSize": "17px", "fontWeight": "700", "color": COLORS["primary_dark"], "marginTop": "8px", "marginBottom": "4px"}),
                        html.P(meta.get("desc", ""), style={"fontSize": "12.5px", "color": "#4A5568", "lineHeight": "1.55", "margin": "0 0 14px 0", "maxWidth": "850px"}),
                    ]),
                ],
            ),
            # Grid Spesifikasi Teknis
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                    "gap": "12px",
                    "backgroundColor": "#F8FAFC",
                    "padding": "12px 16px",
                    "borderRadius": "8px",
                    "border": "1px solid #EDF2F7",
                },
                children=[
                    html.Div([
                        html.Div("Sumber Resmi", style={"fontSize": "10.5px", "color": "#718096", "fontWeight": "600"}),
                        html.Div(meta.get("source", "BPS"), style={"fontSize": "12px", "fontWeight": "600", "color": COLORS["primary_dark"]}),
                    ]),
                    html.Div([
                        html.Div("Cakupan Wilayah", style={"fontSize": "10.5px", "color": "#718096", "fontWeight": "600"}),
                        html.Div(meta.get("scope", "Provinsi"), style={"fontSize": "12px", "fontWeight": "600", "color": COLORS["primary_dark"]}),
                    ]),
                    html.Div([
                        html.Div("Satuan / Unit", style={"fontSize": "10.5px", "color": "#718096", "fontWeight": "600"}),
                        html.Div(meta.get("units", "-"), style={"fontSize": "12px", "fontWeight": "600", "color": COLORS["primary_dark"]}),
                    ]),
                    html.Div([
                        html.Div("Periode Waktu", style={"fontSize": "10.5px", "color": "#718096", "fontWeight": "600"}),
                        html.Div(meta.get("period", "-"), style={"fontSize": "12px", "fontWeight": "600", "color": COLORS["primary_dark"]}),
                    ]),
                    html.Div([
                        html.Div("Dimensi Matriks", style={"fontSize": "10.5px", "color": "#718096", "fontWeight": "600"}),
                        html.Div(f"{len(df_raw):,} baris × {len(df_raw.columns)} kolom", style={"fontSize": "12px", "fontWeight": "700", "color": COLORS["primary"]}),
                    ]),
                ],
            ),
        ],
    )

    # 2. Pembersihan & Format Tampilan untuk DataTable
    display_df = df_raw.copy()
    col_labels = meta.get("column_labels", {})

    # Format nilai numerik agar enak dibaca (desimal rapi dan pemisah ribuan)
    for c in display_df.columns:
        if pd.api.types.is_float_dtype(display_df[c]):
            display_df[c] = display_df[c].apply(lambda v: f"{v:,.2f}" if pd.notna(v) else "-")
        elif pd.api.types.is_integer_dtype(display_df[c]):
            if "penduduk" in c:
                display_df[c] = display_df[c].apply(lambda v: f"{v:,}" if pd.notna(v) else "-")
        else:
            display_df[c] = display_df[c].fillna("-")

    # Siapkan Kolom dengan Header Manusiawi
    columns = [
        {
            "name": col_labels.get(c, c),
            "id": c,
        }
        for c in display_df.columns
    ]

    # Bangun Dash DataTable
    table = dash_table.DataTable(
        data=display_df.to_dict("records"),
        columns=columns,
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto", "border": "1px solid #E2E8F0", "borderRadius": "8px"},
        style_cell={
            "fontFamily": "Inter, sans-serif",
            "fontSize": "12.5px",
            "padding": "9px 12px",
            "textAlign": "left",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": COLORS["primary"],
            "color": "white",
            "fontWeight": "600",
            "fontSize": "12px",
            "borderBottom": "2px solid #0C203A",
        },
        style_data={
            "backgroundColor": "white",
            "color": COLORS["gray_dark"],
            "borderBottom": "1px solid #EDF2F7",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#F8FAFC"},
            {"if": {"state": "active"}, "backgroundColor": "rgba(242, 183, 5, 0.15)", "border": f"1px solid {COLORS['accent']}"},
        ],
    )

    badge_text = f"Menampilkan {len(df_raw):,} Baris Data"
    return meta_card, badge_text, table


# ─────────────────────────────────────────────────────────────────────────────
# Callback Download CSV
# ─────────────────────────────────────────────────────────────────────────────
@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download-csv", "n_clicks"),
    State("explorer-dataset", "value"),
    prevent_initial_call=True,
)
def download_dataset_csv(n_clicks, dataset_key):
    if not n_clicks or not dataset_key:
        return dash.no_update
    df = DATA.get(dataset_key, pd.DataFrame())
    if df.empty:
        return dash.no_update
    filename = f"{dataset_key}_kepri_2021_2025.csv"
    return dcc.send_data_frame(df.to_csv, filename, index=False)

