import json
from pathlib import Path

import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list
from utils.analysis import hitung_laju_pertumbuhan
from theme import COLORS, KABKOTA_COLORS

dash.register_page(__name__, path="/", name="Beranda")

_BASE_DIR = Path(__file__).resolve().parent.parent
_GEOJSON_PATH = _BASE_DIR / "data" / "kepri_kabkota.geojson"

with open(_GEOJSON_PATH, "r", encoding="utf-8") as f:
    _GEOJSON = json.load(f)

# Titik koordinat centroid untuk label nama kabupaten/kota di atas peta
_CENTROIDS = {
    "Kabupaten Karimun": {"lat": 0.88, "lon": 103.42, "short": "Karimun"},
    "Kabupaten Bintan": {"lat": 1.05, "lon": 104.58, "short": "Bintan"},
    "Kabupaten Natuna": {"lat": 3.90, "lon": 108.20, "short": "Natuna"},
    "Kabupaten Lingga": {"lat": -0.15, "lon": 104.60, "short": "Lingga"},
    "Kabupaten Kepulauan Anambas": {"lat": 3.05, "lon": 106.00, "short": "Anambas"},
    "Kota Batam": {"lat": 1.05, "lon": 104.03, "short": "Batam"},
    "Kota Tanjungpinang": {"lat": 0.92, "lon": 104.46, "short": "Tanjungpinang"},
}

years = get_years_list()
latest_year = max(years) if years else 2025

# Skala warna konsisten tema: Biru Tua (#0C203A) -> Navy (#173A66) -> Emas (#C99204) -> Kuning Aksen (#F2B705)
BLUE_YELLOW_SCALE = [
    (0.0, "#0C203A"),
    (0.40, "#173A66"),
    (0.72, "#C99204"),
    (1.0, "#F2B705"),
]

layout = html.Div(
    [
        # ── 1. Hero Card Banner Lebar Penuh (Tanpa Card Kecil-Kecil) ──────────
        html.Div(
            className="home-top-row",
            children=[
                html.Div(
                    className="hero-card",
                    children=[
                        html.Div(
                            className="hero-text",
                            children=[
                                html.H2(
                                    "Sistem Informasi & Analisis PDRB Kepulauan Riau",
                                    className="hero-title",
                                ),
                                html.P(
                                    "Eksplorasi visual dan analisis komprehensif struktur ekonomi riil, disparitas wilayah, "
                                    "sumber pertumbuhan, serta indikator makroekonomi 7 Kabupaten/Kota di Provinsi Kepulauan Riau (2021–2025).",
                                    className="hero-subtitle",
                                ),
                                html.Div(
                                    className="hero-buttons-container",
                                    children=[
                                        dcc.Link(
                                            "Pantau Perilaku Ekonomi →",
                                            href="/monitoring",
                                            className="hero-button",
                                        ),
                                        dcc.Link(
                                            "Analisis Antar Wilayah & Sektoral →",
                                            href="/wilayah",
                                            className="hero-button-outline",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Img(src="/assets/maskot_1.webp", className="hero-mascot"),
                    ],
                )
            ],
        ),

        # ── 2. Kontrol Filter Peta & Komparasi ─────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"minWidth": "280px"},
                    children=[
                        html.Label("Indikator Spasial", className="filter-label"),
                        dcc.Dropdown(
                            id="home-map-indikator",
                            options=[
                                {"label": "PDRB Riil ADHK 2010 (Miliar Rp)", "value": "adhk"},
                                {"label": "PDRB Per Kapita Riil (Juta Rp/jiwa)", "value": "perkapita"},
                                {"label": "Laju Pertumbuhan Ekonomi Riil (%)", "value": "pertumbuhan"},
                            ],
                            value="adhk",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"minWidth": "160px"},
                    children=[
                        html.Label("Tahun Analisis", className="filter-label"),
                        dcc.Dropdown(
                            id="home-map-tahun",
                            options=[{"label": str(y), "value": y} for y in years],
                            value=latest_year,
                            clearable=False,
                        ),
                    ],
                ),
            ],
        ),

        # ── 3. Baris Peta Spasial & Grafik Peringkat Daerah ───────────────────
        html.Div(
            className="home-map-row",
            children=[
                # Peta Spasial (Sisi Kiri)
                html.Div(
                    className="home-map-card",
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "12px"},
                            children=[
                                html.H3("Peta Sebaran Ekonomi Kepulauan Riau", className="card-title", style={"margin": 0}),
                                html.Span(
                                    id="home-map-badge",
                                    style={
                                        "fontSize": "11.5px",
                                        "fontWeight": "600",
                                        "color": COLORS["primary"],
                                        "backgroundColor": "rgba(23, 58, 102, 0.08)",
                                        "padding": "4px 10px",
                                        "borderRadius": "6px",
                                    },
                                ),
                            ],
                        ),
                        dcc.Graph(
                            id="home-spatial-map",
                            config={"displayModeBar": False},
                            style={"height": "480px"},
                        ),
                    ],
                ),
                # Grafik Peringkat Daerah & Benchmark (Sisi Kanan)
                html.Div(
                    className="home-ranking-card",
                    children=[
                        html.H3("Peringkat Kabupaten / Kota", className="card-title", style={"marginBottom": "12px"}),
                        dcc.Graph(
                            id="home-ranking-chart",
                            config={"displayModeBar": False},
                            style={"height": "350px"},
                        ),
                        # Mini Summary Badges
                        html.Div(id="home-map-kpis", style={"marginTop": "auto", "paddingTop": "14px"}),
                    ],
                ),
            ],
        ),

        # ── 4. Modul Navigasi Analisis Cepat (Kartu Biru Tua Transisi) ─────────
        html.Div(
            className="home-modules-grid",
            children=[
                dcc.Link(
                    href="/monitoring",
                    className="home-module-card",
                    children=[
                        html.Div([
                            html.Div("6 Sub-Tab Analisis", className="home-module-tag"),
                            html.H4("Monitoring Perilaku Ekonomi", className="home-module-title"),
                            html.P(
                                "Nilai nominal PDRB, tren laju pertumbuhan, kontribusi 17 sektor, PDRB perkapita, dekomposisi sumber pertumbuhan (SOG), dan indeks implisit.",
                                className="home-module-desc",
                            ),
                        ]),
                        html.Div(["Buka Modul Monitoring ", html.Span("→")], className="home-module-arrow"),
                    ],
                ),
                dcc.Link(
                    href="/wilayah",
                    className="home-module-card",
                    children=[
                        html.Div([
                            html.Div("5 Metode Regional", className="home-module-tag"),
                            html.H4("Analisis Antar Wilayah & Sektoral", className="home-module-title"),
                            html.P(
                                "Indeks ketimpangan Williamson & Bonet, identifikasi keunggulan kompetitif Shift-Share, Tipologi Klassen, dan Location Quotient (LQ).",
                                className="home-module-desc",
                            ),
                        ]),
                        html.Div(["Buka Analisis Wilayah ", html.Span("→")], className="home-module-arrow"),
                    ],
                ),
                dcc.Link(
                    href="/makro",
                    className="home-module-card",
                    children=[
                        html.Div([
                            html.Div("Makroekonomi & Efisiensi", className="home-module-tag"),
                            html.H4("Analisis Makroekonomi Daerah", className="home-module-title"),
                            html.P(
                                "Karakteristik konsumsi rumah tangga (APC & MPC), rasio penerimaan pajak (Tax Ratio & Buoyancy), ICOR modal, dan elastisitas penyerapan tenaga kerja (ILOR).",
                                className="home-module-desc",
                            ),
                        ]),
                        html.Div(["Buka Analisis Makro ", html.Span("→")], className="home-module-arrow"),
                    ],
                ),
            ],
        ),
    ]
)


# ── Callbacks ─────────────────────────────────────────────────────────────
@callback(
    Output("home-spatial-map", "figure"),
    Output("home-ranking-chart", "figure"),
    Output("home-map-kpis", "children"),
    Output("home-map-badge", "children"),
    Input("home-map-indikator", "value"),
    Input("home-map-tahun", "value"),
)
def update_beranda_visuals(indikator, tahun):
    df_pdrb = DATA["pdrb"]
    df_pk = DATA["perkapita"]

    # 1. Total PDRB ADHK per kab/kota
    sub_pdrb = df_pdrb[(df_pdrb["kab_kota"] != PROVINSI_LABEL) & (df_pdrb["tahun"] == tahun)]
    agg_pdrb = sub_pdrb.groupby("kab_kota", as_index=False)["adhk"].sum()

    # 2. PDRB Perkapita
    sub_pk = df_pk[(df_pk["kab_kota"] != PROVINSI_LABEL) & (df_pk["tahun"] == tahun)][
        ["kab_kota", "perkapita_adhk_juta", "perkapita_adhb_juta"]
    ]

    # 3. Laju Pertumbuhan
    growth_df = hitung_laju_pertumbuhan(df_pdrb)
    sub_growth = growth_df[(growth_df["kab_kota"] != PROVINSI_LABEL) & (growth_df["tahun"] == tahun)][
        ["kab_kota", "laju_pertumbuhan"]
    ]

    # Gabungkan Data Kabupaten/Kota
    df_m = pd.merge(agg_pdrb, sub_pk, on="kab_kota")
    df_m = pd.merge(df_m, sub_growth, on="kab_kota")

    # Ambil Nilai Acuan Provinsi Kepri
    prov_row_pdrb = df_pdrb[(df_pdrb["kab_kota"] == PROVINSI_LABEL) & (df_pdrb["tahun"] == tahun)]
    prov_adhk = prov_row_pdrb["adhk"].sum() if not prov_row_pdrb.empty else 0.0

    prov_row_pk = df_pk[(df_pk["kab_kota"] == PROVINSI_LABEL) & (df_pk["tahun"] == tahun)]
    prov_pk = prov_row_pk["perkapita_adhk_juta"].iloc[0] if not prov_row_pk.empty else 0.0

    prov_row_growth = growth_df[(growth_df["kab_kota"] == PROVINSI_LABEL) & (growth_df["tahun"] == tahun)]
    prov_growth = prov_row_growth["laju_pertumbuhan"].iloc[0] if not prov_row_growth.empty else 0.0

    # Tentukan Kolom, Label, dan Format
    if indikator == "adhk":
        target_col = "adhk"
        label_metrik = "PDRB Riil ADHK"
        unit = "Miliar Rp"
        val_format = ":,.1f"
        prov_val = prov_adhk
        badge_text = f"PDRB ADHK • Tahun {tahun}"
    elif indikator == "perkapita":
        target_col = "perkapita_adhk_juta"
        label_metrik = "PDRB Per Kapita Riil"
        unit = "Juta Rp/jiwa"
        val_format = ":,.2f"
        prov_val = prov_pk
        badge_text = f"Per Kapita ADHK • Tahun {tahun}"
    else:
        target_col = "laju_pertumbuhan"
        label_metrik = "Laju Pertumbuhan Riil"
        unit = "%"
        val_format = ":.2f"
        prov_val = prov_growth
        badge_text = f"Pertumbuhan • Tahun {tahun}"

    df_m["display_val"] = df_m[target_col]

    # ── Bangun Peta Choropleth Interaktif ─────────────────────────────────
    map_args = dict(
        geojson=_GEOJSON,
        locations="kab_kota",
        featureidkey="properties.kab_kota",
        color="display_val",
        color_continuous_scale=BLUE_YELLOW_SCALE,
        center={"lat": 2.1, "lon": 106.0},
        zoom=5.1,
        opacity=0.88,
        hover_name="kab_kota",
        hover_data={
            "kab_kota": False,
            "display_val": val_format,
            "adhk": ":,.1f",
            "perkapita_adhk_juta": ":.2f",
            "laju_pertumbuhan": ":.2f",
        },
        labels={
            "display_val": f"{label_metrik} ({unit})",
            "adhk": "PDRB ADHK (M)",
            "perkapita_adhk_juta": "Per Kapita (Jt)",
            "laju_pertumbuhan": "Laju (%)",
        },
    )

    if hasattr(px, "choropleth_map"):
        fig_map = px.choropleth_map(df_m, map_style="carto-positron", **map_args)
        fig_map.add_trace(
            go.Scattermap(
                lat=[_CENTROIDS[k]["lat"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                lon=[_CENTROIDS[k]["lon"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                mode="text",
                text=[_CENTROIDS[k]["short"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                textfont=dict(size=11, color="#0C203A", family="Inter, sans-serif"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    else:
        fig_map = px.choropleth_mapbox(df_m, mapbox_style="carto-positron", **map_args)
        fig_map.add_trace(
            go.Scattermapbox(
                lat=[_CENTROIDS[k]["lat"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                lon=[_CENTROIDS[k]["lon"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                mode="text",
                text=[_CENTROIDS[k]["short"] for k in df_m["kab_kota"] if k in _CENTROIDS],
                textfont=dict(size=11, color="#0C203A", family="Inter, sans-serif"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    if len(fig_map.data) > 0 and hasattr(fig_map.data[0], "marker") and hasattr(fig_map.data[0].marker, "line"):
        fig_map.data[0].marker.line.width = 1.5
        fig_map.data[0].marker.line.color = "rgba(255, 255, 255, 0.95)"
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=f"{unit}",
            thickness=14,
            len=0.75,
            x=0.98,
            xanchor="right",
            y=0.5,
            title_font=dict(size=11),
            tickfont=dict(size=10),
        ),
    )

    # ── Bangun Grafik Batang Peringkat Daerah ─────────────────────────────
    df_sorted = df_m.sort_values("display_val", ascending=True).reset_index(drop=True)
    bar_colors = [KABKOTA_COLORS.get(kk, COLORS["primary"]) for kk in df_sorted["kab_kota"]]

    if indikator == "adhk":
        bar_text = [f"Rp {v:,.1f} M" for v in df_sorted["display_val"]]
    elif indikator == "perkapita":
        bar_text = [f"Rp {v:,.1f} Jt" for v in df_sorted["display_val"]]
    else:
        bar_text = [f"{v:+.2f}%" for v in df_sorted["display_val"]]

    fig_rank = go.Figure(
        go.Bar(
            y=df_sorted["kab_kota"],
            x=df_sorted["display_val"],
            orientation="h",
            marker=dict(color=bar_colors),
            text=bar_text,
            textposition="outside",
            hovertemplate=f"<b>%{{y}}</b><br>{label_metrik}: %{{x{val_format}}} {unit}<extra></extra>",
        )
    )

    # Tambahkan garis acuan provinsi jika indikator bukan total volume PDRB
    if indikator != "adhk" and prov_val > 0:
        fig_rank.add_vline(
            x=prov_val,
            line_dash="dash",
            line_color=COLORS["accent_dark"],
            line_width=2,
            annotation_text=f"Rata-rata Kepri: {prov_val:.2f}{unit}",
            annotation_position="top right",
            annotation_font=dict(size=10, color=COLORS["accent_dark"]),
        )

    fig_rank.update_layout(
        margin=dict(l=10, r=80, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#EFEFEF", title=f"{label_metrik} ({unit})"),
        yaxis=dict(showgrid=False, title=""),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # ── Bangun Mini Summary Badges ────────────────────────────────────────
    top_row = df_sorted.iloc[-1]
    bot_row = df_sorted.iloc[0]

    if indikator == "adhk":
        top_txt = f"Rp {top_row['display_val']:,.1f} M"
        bot_txt = f"Rp {bot_row['display_val']:,.1f} M"
        prov_txt = f"Rp {prov_val:,.1f} M (Total)"
    elif indikator == "perkapita":
        top_txt = f"Rp {top_row['display_val']:.1f} Jt"
        bot_txt = f"Rp {bot_row['display_val']:.1f} Jt"
        prov_txt = f"Rp {prov_val:.1f} Jt (Rata-rata)"
    else:
        top_txt = f"{top_row['display_val']:+.2f}%"
        bot_txt = f"{bot_row['display_val']:+.2f}%"
        prov_txt = f"{prov_val:+.2f}% (Kepri)"

    summary_badges = html.Div(
        style={"display": "flex", "gap": "10px", "justifyContent": "space-between", "flexWrap": "wrap"},
        children=[
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "100px",
                    "padding": "10px 14px",
                    "backgroundColor": "rgba(242, 183, 5, 0.12)",
                    "borderRadius": "8px",
                    "borderLeft": f"3px solid {COLORS['accent']}",
                },
                children=[
                    html.Div("TERTINGGI", style={"fontSize": "10px", "fontWeight": "700", "color": COLORS["accent_dark"]}),
                    html.Div(f"{top_row['kab_kota']}", style={"fontSize": "12px", "fontWeight": "700", "color": COLORS["primary_dark"]}),
                    html.Div(top_txt, style={"fontSize": "13px", "fontWeight": "700", "color": COLORS["primary"]}),
                ],
            ),
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "100px",
                    "padding": "10px 14px",
                    "backgroundColor": "rgba(23, 58, 102, 0.08)",
                    "borderRadius": "8px",
                    "borderLeft": f"3px solid {COLORS['primary']}",
                },
                children=[
                    html.Div("ACUAN PROVINSI", style={"fontSize": "10px", "fontWeight": "700", "color": COLORS["primary"]}),
                    html.Div("Provinsi Kepri", style={"fontSize": "12px", "fontWeight": "700", "color": COLORS["primary_dark"]}),
                    html.Div(prov_txt, style={"fontSize": "13px", "fontWeight": "700", "color": COLORS["primary"]}),
                ],
            ),
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "100px",
                    "padding": "10px 14px",
                    "backgroundColor": "#F7F7F7",
                    "borderRadius": "8px",
                    "borderLeft": "3px solid #9B9B9B",
                },
                children=[
                    html.Div("TERENDAH", style={"fontSize": "10px", "fontWeight": "700", "color": "#757575"}),
                    html.Div(f"{bot_row['kab_kota']}", style={"fontSize": "12px", "fontWeight": "700", "color": COLORS["primary_dark"]}),
                    html.Div(bot_txt, style={"fontSize": "13px", "fontWeight": "700", "color": COLORS["primary_dark"]}),
                ],
            ),
        ],
    )

    return fig_map, fig_rank, summary_badges, badge_text
