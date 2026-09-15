"""
Tab Tipologi Klassen - Kepulauan Riau
Sumber data: data/Tipologi_Klassen_Kepri_2021-2025.xlsx
Peta Spasial: data/kepri_kabkota.geojson
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.components import card
from theme import REFERENCE_LINE_STYLE, COLORS, CATEGORY_PALETTE

# ---------------------------------------------------------------------------
# Load dan bersihkan data
# ---------------------------------------------------------------------------
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_DATA_PATH = _BASE_DIR / "data" / "Tipologi_Klassen_Kepri_2021-2025.xlsx"
_GEOJSON_PATH = _BASE_DIR / "data" / "kepri_kabkota.geojson"

_PROVINSI  = "Provinsi Kepulauan Riau"
_KAB_VALID = [
    "Kabupaten Karimun",
    "Kabupaten Bintan",
    "Kabupaten Natuna",
    "Kabupaten Lingga",
    "Kabupaten Kepulauan Anambas",
    "Kota Batam",
    "Kota Tanjungpinang",
    _PROVINSI,
]
_KAB_ONLY = [k for k in _KAB_VALID if k != _PROVINSI]

# Load GeoJSON untuk Peta
with open(_GEOJSON_PATH, "r", encoding="utf-8") as f:
    _GEOJSON = json.load(f)

# Koordinat centroid untuk label nama di peta
_CENTROIDS = {
    "Kabupaten Karimun": {"lat": 0.88, "lon": 103.42, "short": "Karimun"},
    "Kabupaten Bintan": {"lat": 1.05, "lon": 104.58, "short": "Bintan"},
    "Kabupaten Natuna": {"lat": 3.90, "lon": 108.20, "short": "Natuna"},
    "Kabupaten Lingga": {"lat": -0.15, "lon": 104.60, "short": "Lingga"},
    "Kabupaten Kepulauan Anambas": {"lat": 3.05, "lon": 106.00, "short": "Anambas"},
    "Kota Batam": {"lat": 1.05, "lon": 104.03, "short": "Batam"},
    "Kota Tanjungpinang": {"lat": 0.92, "lon": 104.46, "short": "Tanjungpinang"},
}

_xl = pd.ExcelFile(_DATA_PATH)

_df_pdrb = _xl.parse("1. Data PDRB ADHK", header=0)
_df_pdrb = (
    _df_pdrb[_df_pdrb["Kabupaten_Kota"].isin(_KAB_VALID)]
    .dropna(subset=["Lapangan_Usaha"])
    .copy()
)
_TAHUN_COLS_INT = sorted(
    [int(c) for c in _df_pdrb.columns if isinstance(c, (int, float)) and 2020 <= int(c) <= 2025]
)

_df_pop = _xl.parse("2. Data Penduduk", header=0)
_df_pop = (
    _df_pop[_df_pop["Kabupaten_Kota"].isin(_KAB_VALID)]
    .dropna(subset=["Kabupaten_Kota"])
    .set_index("Kabupaten_Kota")
)

# Urutan lapangan usaha berdasarkan kode (A s.d. R,S,T,U)
_KODE_ORDER = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M,N", "O", "P", "Q", "R,S,T,U"]
_lu_kode_map = (
    _df_pdrb[["Kode", "Lapangan_Usaha"]]
    .dropna()
    .drop_duplicates("Kode")
    .set_index("Kode")["Lapangan_Usaha"]
    .to_dict()
)
_LAPANGAN_USAHA_LIST = [
    _lu_kode_map[k] for k in _KODE_ORDER if k in _lu_kode_map
]
_TAHUN_OPTIONS = [t for t in _TAHUN_COLS_INT if t >= 2021]

# Palet 4 warna harmonis Tipologi Klassen:
# 1. Hijau Emerald: Maju & Tumbuh Cepat (simbol kemakmuran)
# 2. Biru Navy: Sedang Berkembang (warna identitas dashboard)
# 3. Kuning Emas: Maju Tapi Tertekan (warna aksen dashboard)
# 4. Coral / Terracotta: Relatif Tertinggal (warna hangat penarik perhatian)
_KUADRAN_COLORS = {
    "I - Maju dan Tumbuh Cepat" : "#10B981",  # Hijau Emerald
    "II - Sedang Berkembang"    : "#173A66",  # Biru Navy Khas Dashboard
    "III - Maju Tapi Tertekan"  : "#F2B705",  # Kuning Emas / Amber
    "IV - Relatif Tertinggal"   : "#E76F51",  # Coral / Terracotta Elegan
}


# ---------------------------------------------------------------------------
# Fungsi kalkulasi
# ---------------------------------------------------------------------------
def _hitung_klassen(tahun: int, lu_filter):
    tahun_prev = tahun - 1

    if lu_filter:
        pdrb_sub = _df_pdrb[_df_pdrb["Lapangan_Usaha"].isin(lu_filter)]
    else:
        pdrb_sub = _df_pdrb

    total_t      = pdrb_sub.groupby("Kabupaten_Kota")[tahun].sum()
    total_t_prev = pdrb_sub.groupby("Kabupaten_Kota")[tahun_prev].sum()
    pop_t        = _df_pop[tahun]

    perkapita = (total_t / pop_t).rename("pdrb_perkapita")
    laju      = ((total_t - total_t_prev) / total_t_prev * 100).rename("laju_pertumbuhan")

    # Referensi provinsi dari agregat kab/kota
    sub_kab          = pdrb_sub[pdrb_sub["Kabupaten_Kota"].isin(_KAB_ONLY)]
    ref_pdrb_t       = sub_kab.groupby("Kabupaten_Kota")[tahun].sum().sum()
    ref_pdrb_t_prev  = sub_kab.groupby("Kabupaten_Kota")[tahun_prev].sum().sum()
    ref_pop_t        = _df_pop.loc[_PROVINSI, tahun]
    ref_perkapita    = ref_pdrb_t / ref_pop_t
    ref_laju         = (ref_pdrb_t - ref_pdrb_t_prev) / ref_pdrb_t_prev * 100

    df = pd.DataFrame({
        "kab_kota"        : perkapita.index,
        "pdrb_perkapita"  : perkapita.values,
        "laju_pertumbuhan": laju.reindex(perkapita.index).values,
    })
    df = df[df["kab_kota"].isin(_KAB_ONLY)].copy()

    def _klas(row):
        a = row["laju_pertumbuhan"] >= ref_laju
        b = row["pdrb_perkapita"] >= ref_perkapita
        if a and b:
            return "I - Maju dan Tumbuh Cepat"
        elif a and not b:
            return "II - Sedang Berkembang"
        elif not a and b:
            return "III - Maju Tapi Tertekan"
        else:
            return "IV - Relatif Tertinggal"

    df["kuadran"] = df.apply(_klas, axis=1)
    return df, ref_perkapita, ref_laju


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def layout():
    lu_options = [{"label": "Keseluruhan", "value": "__all__"}] + [
        {"label": f"{kode} - {_lu_kode_map[kode]}", "value": _lu_kode_map[kode]}
        for kode in _KODE_ORDER if kode in _lu_kode_map
    ]
    return html.Div([
        # ── Filter row ─────────────────────────────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"flex": "2", "minWidth": "280px"},
                    children=[
                        html.Label("Lapangan Usaha", className="filter-label"),
                        dcc.Dropdown(
                            id="klassen-lu",
                            options=lu_options,
                            value="__all__",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"flex": "1", "minWidth": "140px"},
                    children=[
                        html.Label("Tahun", className="filter-label"),
                        dcc.Dropdown(
                            id="klassen-tahun",
                            options=[{"label": str(t), "value": t} for t in _TAHUN_OPTIONS],
                            value=max(_TAHUN_OPTIONS),
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"flex": "1.5", "minWidth": "240px"},
                    children=[
                        html.Label("Mode Tampilan", className="filter-label"),
                        dcc.RadioItems(
                            id="klassen-view-mode",
                            options=[
                                {"label": " Diagram & Peta", "value": "both"},
                                {"label": " Diagram", "value": "chart"},
                                {"label": " Peta", "value": "map"},
                            ],
                            value="both",
                            inline=True,
                            style={
                                "display": "flex",
                                "gap": "16px",
                                "alignItems": "center",
                                "height": "38px",
                                "fontSize": "13px",
                                "fontWeight": "500",
                            },
                        ),
                    ],
                ),
            ],
        ),

        # ── Visualisasi: Diagram & Peta dalam Flexbox ────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                # Kartu Diagram Kuadran
                html.Div(
                    id="klassen-chart-container",
                    className="card-box",
                    style={"flex": "1", "minWidth": "420px", "marginBottom": "0"},
                    children=[
                        html.Div(id="klassen-judul", className="card-title"),
                        dcc.Graph(id="graf-klassen", style={"height": "500px"}),
                    ],
                ),
                # Kartu Peta Spasial
                html.Div(
                    id="klassen-map-container",
                    className="card-box",
                    style={"flex": "1", "minWidth": "420px", "marginBottom": "0"},
                    children=[
                        html.Div(id="klassen-map-judul", className="card-title"),
                        dcc.Graph(id="map-klassen", style={"height": "500px"}),
                    ],
                ),
            ],
        ),

        # ── Tabel Ringkasan Klasifikasi ─────────────────────────────────────
        card("Ringkasan Klasifikasi Wilayah", html.Div(id="klassen-tabel")),
    ])


# ---------------------------------------------------------------------------
# Callback
# ---------------------------------------------------------------------------
@callback(
    Output("graf-klassen",           "figure"),
    Output("map-klassen",            "figure"),
    Output("klassen-chart-container", "style"),
    Output("klassen-map-container",   "style"),
    Output("klassen-judul",          "children"),
    Output("klassen-map-judul",      "children"),
    Output("klassen-tabel",          "children"),
    Input("klassen-lu",              "value"),
    Input("klassen-tahun",           "value"),
    Input("klassen-view-mode",       "value"),
)
def update_klassen(lu_val, tahun, view_mode):
    if lu_val == "__all__" or not lu_val:
        lu_filter = None
        lu_label  = "Keseluruhan Lapangan Usaha"
    else:
        lu_filter = [lu_val]
        lu_label  = lu_val

    df, ref_perkapita, ref_laju = _hitung_klassen(tahun, lu_filter)

    # ── 1. Scatter Plot (Kuadran) ──────────────────────────────────────────
    fig_chart = px.scatter(
        df,
        x="pdrb_perkapita",
        y="laju_pertumbuhan",
        color="kuadran",
        text="kab_kota",
        color_discrete_map=_KUADRAN_COLORS,
        labels={
            "pdrb_perkapita"  : "PDRB Per Kapita (Juta Rp/Jiwa)",
            "laju_pertumbuhan": "Laju Pertumbuhan PDRB (%)",
            "kuadran"         : "Kuadran",
        },
        hover_data={
            "pdrb_perkapita"  : ":.3f",
            "laju_pertumbuhan": ":.2f",
            "kuadran"         : True,
            "kab_kota"        : False,
        },
    )
    fig_chart.update_traces(textposition="top center", marker=dict(size=14))

    # Garis referensi
    fig_chart.add_vline(x=ref_perkapita, line=REFERENCE_LINE_STYLE)
    fig_chart.add_hline(y=ref_laju, line=REFERENCE_LINE_STYLE)

    # Nilai referensi
    x_min = df["pdrb_perkapita"].min()
    x_max = df["pdrb_perkapita"].max()
    y_min = df["laju_pertumbuhan"].min()
    y_max = df["laju_pertumbuhan"].max()

    fig_chart.add_annotation(
        x=ref_perkapita, y=y_max,
        text=f"Provinsi: {ref_perkapita:.2f}",
        showarrow=False, xanchor="left", yanchor="bottom",
        font=dict(size=10, color=COLORS["accent_dark"]),
    )
    fig_chart.add_annotation(
        x=x_max, y=ref_laju,
        text=f"Provinsi: {ref_laju:.2f}%",
        showarrow=False, xanchor="right", yanchor="bottom",
        font=dict(size=10, color=COLORS["accent_dark"]),
    )

    # Label nomor kuadran di sudut
    pad_x = (x_max - x_min) * 0.03
    pad_y = (y_max - y_min) * 0.03
    for xp, yp, xa, ya, lbl in [
        (x_max - pad_x, y_max - pad_y, "right", "top",    "I"),
        (x_min + pad_x, y_max - pad_y, "left",  "top",    "II"),
        (x_max - pad_x, y_min + pad_y, "right", "bottom", "III"),
        (x_min + pad_x, y_min + pad_y, "left",  "bottom", "IV"),
    ]:
        fig_chart.add_annotation(
            x=xp, y=yp, text=lbl,
            showarrow=False, xanchor=xa, yanchor=ya,
            font=dict(size=26, color=COLORS["gray_light"], family="Arial Black"),
        )

    fig_chart.update_layout(
        margin=dict(l=60, r=25, t=30, b=105),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=11),
        ),
    )

    # ── 2. Peta Spasial (Choropleth Map dengan Base Satelit Halus) ──────────
    fig_map = px.choropleth_map(
        df,
        geojson=_GEOJSON,
        locations="kab_kota",
        featureidkey="properties.kab_kota",
        color="kuadran",
        color_discrete_map=_KUADRAN_COLORS,
        map_style="white-bg",
        center={"lat": 2.1, "lon": 106.0},
        zoom=5.4,
        opacity=0.68,
        hover_name="kab_kota",
        hover_data={
            "kab_kota": False,
            "kuadran": True,
            "pdrb_perkapita": ":.2f",
            "laju_pertumbuhan": ":.2f",
        },
        labels={
            "kuadran": "Kuadran",
            "pdrb_perkapita": "PDRB Per Kapita (Jt Rp)",
            "laju_pertumbuhan": "Laju Pertumbuhan (%)",
        },
    )

    # Garis tepi pulau dibuat putih tegas agar kontras di atas citra satelit
    fig_map.update_traces(
        marker_line_width=1.5,
        marker_line_color="rgba(255, 255, 255, 0.95)",
    )

    # Label nama wilayah dengan titik dan teks putih kontras
    lat_labels = [_CENTROIDS[k]["lat"] for k in df["kab_kota"] if k in _CENTROIDS]
    lon_labels = [_CENTROIDS[k]["lon"] for k in df["kab_kota"] if k in _CENTROIDS]
    text_labels = [_CENTROIDS[k]["short"] for k in df["kab_kota"] if k in _CENTROIDS]

    fig_map.add_trace(
        go.Scattermap(
            lat=lat_labels,
            lon=lon_labels,
            mode="text+markers",
            text=text_labels,
            marker=dict(size=4, color="white"),
            textfont=dict(size=11, color="#FFFFFF", family="Inter, sans-serif"),
            textposition="top center",
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Base peta satelit (gaya Google Satellite) dengan opacity 0.72 agar elegan dan tidak ngejreng
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=10, b=75),
        map=dict(
            style="white-bg",
            layers=[
                dict(
                    below="traces",
                    sourcetype="raster",
                    source=[
                        "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                    ],
                    opacity=0.72,  # Subdued / lembut, tidak terlalu mencolok/ngejreng
                )
            ],
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.03,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=11),
        ),
    )

    # ── 3. Pengaturan Tampilan (Visibility) ────────────────────────────────
    base_box_style = {"borderRadius": "8px", "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "padding": "18px 20px", "backgroundColor": COLORS["white"]}
    
    if view_mode == "chart":
        chart_style = {**base_box_style, "display": "block", "flex": "1", "width": "100%"}
        map_style   = {"display": "none"}
    elif view_mode == "map":
        chart_style = {"display": "none"}
        map_style   = {**base_box_style, "display": "block", "flex": "1", "width": "100%"}
    else:  # "both"
        chart_style = {**base_box_style, "display": "block", "flex": "1", "minWidth": "420px"}
        map_style   = {**base_box_style, "display": "block", "flex": "1", "minWidth": "420px"}

    # ── 4. Judul ──────────────────────────────────────────────────────────
    judul_chart = f"Diagram Tipologi Klassen {tahun} — {lu_label}"
    judul_map   = f"Peta Sebaran Kuadran {tahun} — {lu_label}"

    # ── 5. Tabel Ringkasan ────────────────────────────────────────────────
    kuadran_defs = {
        "I - Maju dan Tumbuh Cepat" : "Pertumbuhan >= Provinsi dan Per Kapita >= Provinsi",
        "II - Sedang Berkembang"    : "Pertumbuhan >= Provinsi dan Per Kapita < Provinsi",
        "III - Maju Tapi Tertekan"  : "Pertumbuhan < Provinsi dan Per Kapita >= Provinsi",
        "IV - Relatif Tertinggal"   : "Pertumbuhan < Provinsi dan Per Kapita < Provinsi",
    }
    header_style = {
        "padding": "8px 12px", "textAlign": "left",
        "borderBottom": f"2px solid {COLORS['gray_light']}",
        "fontWeight": "600",
    }
    rows = []
    for kuadran, definisi in kuadran_defs.items():
        kab_list = df[df["kuadran"] == kuadran]["kab_kota"].tolist()
        warna = _KUADRAN_COLORS.get(kuadran, "#999")
        rows.append(html.Tr([
            html.Td(
                html.Span(kuadran, style={"color": warna, "fontWeight": "600"}),
                style={"padding": "8px 12px", "whiteSpace": "nowrap"},
            ),
            html.Td(definisi, style={"padding": "8px 12px", "color": COLORS["gray_mid"]}),
            html.Td(
                ", ".join(kab_list) if kab_list else "—",
                style={"padding": "8px 12px"},
            ),
        ]))

    tabel = html.Table(
        [
            html.Thead(html.Tr([
                html.Th("Kuadran", style=header_style),
                html.Th("Kriteria", style=header_style),
                html.Th("Kab/Kota", style=header_style),
            ])),
            html.Tbody(rows),
        ],
        style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
    )

    return fig_chart, fig_map, chart_style, map_style, judul_chart, judul_map, tabel
