import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
import pandas as pd

from utils.data_loader import DATA
from utils.components import page_heading
from theme import COLORS

dash.register_page(__name__, path="/explorer", name="Data Explorer")

import dash
from dash import html, dcc, dash_table, callback, Output, Input, State
import pandas as pd

from utils.data_loader import DATA
from utils.components import page_heading
from theme import COLORS

dash.register_page(__name__, path="/explorer", name="Data Explorer")

COLUMN_LABELS = {
    "kab_kota": "Kabupaten / Kota",
    "kode": "Kode",
    "lapangan_usaha": "Lapangan Usaha",
    "tahun": "Tahun",
    "adhk": "ADHK 2010 (Miliar Rp)",
    "adhb": "ADHB (Miliar Rp)",
    "perkapita_adhk_ribu": "ADHK (Ribu Rp)",
    "perkapita_adhb_ribu": "ADHB (Ribu Rp)",
    "perkapita_adhk_juta": "ADHK (Juta Rp)",
    "perkapita_adhb_juta": "ADHB (Juta Rp)",
    "kategori": "Kategori",
    "uraian": "Uraian",
    "pertumbuhan_q_to_q": "Laju q-to-q (%)",
    "pertumbuhan_y_on_y": "Laju y-on-y (%)",
    "sog_q_to_q": "SOG q-to-q (Poin %)",
    "sog_y_on_y": "SOG y-on-y (Poin %)",
    "is_utama": "Sektor Utama",
    "indeks_implisit": "Indeks Deflator (2010=100)",
    "laju_implisit": "Laju Inflasi Implisit (%)",
    "jumlah_penduduk": "Jumlah Penduduk (Jiwa)",
    "penduduk_ribu": "Penduduk (Ribu Jiwa)",
    "pdrb_yd_miliar": "PDRB Yd (Miliar Rp)",
    "konsumsi_c_miliar": "Konsumsi RT (Miliar Rp)",
    "apc": "APC",
    "aps": "APS",
    "pdrb_adhk_miliar": "PDRB ADHK (Miliar Rp)",
    "delta_pdrb_miliar": "Delta PDRB (Miliar Rp)",
    "pmtb_adhk_miliar": "PMTB ADHK (Miliar Rp)",
    "icor": "ICOR",
    "penduduk_bekerja_jiwa": "Penduduk Bekerja (Jiwa)",
    "pertumbuhan_tk_pct": "Pertumbuhan Naker (%)",
    "pertumbuhan_pdrb_pct": "Pertumbuhan PDRB (%)",
    "ilor": "ILOR",
    "etk": "ETK",
    "pdrb_adhb_miliar": "PDRB ADHB (Miliar Rp)",
    "penerimaan_pajak_miliar": "Pajak Daerah (Miliar Rp)",
    "penerimaan_sda_miliar": "Bagi Hasil SDA (Miliar Rp)",
    "total_penerimaan_miliar": "Total Penerimaan (Miliar Rp)",
    "tax_ratio_pct": "Tax Ratio (%)",
    "ekspor_miliar": "Ekspor (Miliar Rp)",
    "impor_miliar": "Impor (Miliar Rp)",
    "neraca_perdagangan_miliar": "Net Ekspor (Miliar Rp)",
    "total_perdagangan_miliar": "Total Perdagangan (Miliar Rp)",
    "rpi": "RPI",
    "pdrb_perkapita_ribu": "Per Kapita (Ribu Rp)",
    "pdrb_perkapita_juta": "Per Kapita (Juta Rp)",
    "bobot_penduduk": "Bobot Penduduk",
    "yn_provinsi_ribu": "Provinsi (Ribu Rp)",
    "yn_provinsi_juta": "Provinsi (Juta Rp)",
    "williamson_provinsi": "Indeks Williamson",
    "indeks_bonet": "Indeks Bonet",
    "deviasi_persen": "Deviasi (%)",
    "kontribusi_disparitas_pct": "Kontribusi (%)",
    "williamson": "Indeks Williamson",
    "bonet_mean": "Bonet (Mean)",
    "bonet_weighted": "Bonet (Weighted)",
    "yn_ribu": "Per Kapita (Ribu Rp)",
    "yn_juta": "Per Kapita (Juta Rp)",
    "total_penduduk": "Total Penduduk",
    "Kabupaten_Kota": "Kabupaten / Kota",
    "Lapangan_Usaha": "Lapangan Usaha",
    "Rerata": "Rerata (%)",
    "N_Rerata": "Komponen N",
    "P_Rerata": "Komponen P",
    "D_Rerata": "Komponen D",
    "Rata_rata": "Rata-rata",
    "Keterangan": "Keterangan",
}

DATASET_OPTIONS = [
    {"label": "PDRB Sektoral (ADHK & ADHB 2010)", "value": "pdrb"},
    {"label": "PDRB Per Kapita", "value": "perkapita"},
    {"label": "Sumber Pertumbuhan Ekonomi (SOG)", "value": "sumber_pertumbuhan"},
    {"label": "Indeks & Laju Implisit", "value": "implisit"},
    {"label": "Jumlah Penduduk", "value": "penduduk"},
    {"label": "Ketimpangan Williamson & Bonet (Kepri)", "value": "williamson_bonet_kepri"},
    {"label": "Ketimpangan Se-Sumatera", "value": "williamson_bonet_sumatera"},
    {"label": "Shift-Share Kabupaten/Kota", "value": "shift_share_kk"},
    {"label": "Location Quotient (LQ)", "value": "lq_kk"},
    {"label": "Konsumsi Rumah Tangga (APC & MPC)", "value": "konsumsi_apc_mpc"},
    {"label": "ICOR & Investasi Modal (PMTB)", "value": "icor"},
    {"label": "ILOR & Elastisitas Tenaga Kerja", "value": "ilor_etk"},
    {"label": "Tax Ratio & Penerimaan Daerah", "value": "tax_ratio"},
    {"label": "Rasio Perdagangan Internasional (RPI)", "value": "perdagangan_internasional"},
]

layout = html.Div(
    [
        page_heading("Data Explorer", "Eksplorasi dan unduh data mentah tabel indikator."),
        html.Div(
            className="filter-row",
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end", "flexWrap": "wrap", "gap": "16px"},
            children=[
                html.Div(
                    className="filter-item",
                    style={"minWidth": "320px", "flex": "1"},
                    children=[
                        html.Label("Pilih Dataset", className="filter-label"),
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
                            "Unduh CSV",
                            id="btn-download-csv",
                            className="hero-button",
                            style={"height": "38px", "padding": "0 20px"},
                        ),
                        dcc.Download(id="download-dataframe-csv"),
                    ]
                ),
            ],
        ),
        html.Div(
            className="card-box",
            children=[
                html.Div(
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "14px"},
                    children=[
                        html.H3("Tabel Data", className="card-title", style={"margin": 0}),
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


@callback(
    Output("explorer-row-count-badge", "children"),
    Output("explorer-table-container", "children"),
    Input("explorer-dataset", "value"),
)
def update_explorer_view(dataset_key):
    df_raw = DATA.get(dataset_key, pd.DataFrame())

    if df_raw.empty:
        empty_box = html.Div(
            "Data tidak tersedia.",
            style={"padding": "30px", "textAlign": "center", "color": COLORS["gray_mid"]},
        )
        return "0 baris", empty_box

    display_df = df_raw.copy()

    for c in display_df.columns:
        if pd.api.types.is_float_dtype(display_df[c]):
            display_df[c] = display_df[c].apply(lambda v: f"{v:,.2f}" if pd.notna(v) else "-")
        elif pd.api.types.is_integer_dtype(display_df[c]):
            if "penduduk" in c:
                display_df[c] = display_df[c].apply(lambda v: f"{v:,}" if pd.notna(v) else "-")
        else:
            display_df[c] = display_df[c].fillna("-")

    columns = [
        {
            "name": COLUMN_LABELS.get(c, c),
            "id": c,
        }
        for c in display_df.columns
    ]

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

    badge_text = f"{len(df_raw):,} baris data"
    return badge_text, table


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
    filename = f"{dataset_key}_kepri.csv"
    return dcc.send_data_frame(df.to_csv, filename, index=False)


