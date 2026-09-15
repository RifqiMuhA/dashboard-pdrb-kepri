"""
Tab ILOR & Elastisitas Tenaga Kerja (ETK) — Provinsi Kepulauan Riau
Sumber data: data/ICOR-ILOR-RPI-TAX.xlsx, Sheet "ILOR & ETK"

ILOR = ΔTK / ΔY  (jumlah TK baru per tambahan PDRB)
ETK  = (%ΔTK) / (%ΔY)  (elastisitas persentase)
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc

from utils.components import card
from theme import COLORS

# ---------------------------------------------------------------------------
# 1. Load Data dari Excel
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ICOR-ILOR-RPI-TAX.xlsx"
_xl = pd.ExcelFile(_DATA_PATH)

# Data sudah diekstrak langsung dari sheet (hardcode nilai yang sudah tervalidasi)
_df_ilor = pd.DataFrame({
    "tahun": [2021, 2022, 2023, 2024, 2025],
    "ilor":  [-4.15, -6.99, 5.10, -1.97, 0.90],
})

_df_etk = pd.DataFrame({
    "tahun":            [2021, 2022, 2023, 2024, 2025],
    "pct_perubahan_tk": [-2.34, -6.17, 5.14, -1.93, 1.31],
    "pct_perubahan_y":  [3.43, 5.06, 5.16, 5.02, 6.94],
    "etk":              [-0.68, -1.22, 1.00, -0.38, 0.19],
})

_df_tk = pd.DataFrame({
    "tahun": [2020, 2021, 2022, 2023, 2024, 2025],
    "jumlah_penduduk_bekerja": [1062004, 1037133, 973125, 1023125, 1003390, 1016540],
    "pdrb_adhk": [174959.2, 180952.44, 190111.09, 199912.8, 209939.1, 224504.7],
})

# Statistik
_n_positif_ilor = ((_df_ilor["ilor"] > 0).sum())
_n_negatif_ilor = ((_df_ilor["ilor"] < 0).sum())
_etk_positif = _df_etk[_df_etk["etk"] > 0]["tahun"].tolist()


# ---------------------------------------------------------------------------
# 2. Builder Grafik
# ---------------------------------------------------------------------------
def _build_grafik_ilor():
    """Bar chart ILOR per tahun dengan warna berbeda pos/neg."""
    bar_colors = [
        COLORS["primary"] if v > 0 else COLORS["accent"]
        for v in _df_ilor["ilor"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_df_ilor["tahun"].astype(str),
        y=_df_ilor["ilor"],
        marker_color=bar_colors,
        text=[f"{v:.2f}" for v in _df_ilor["ilor"]],
        textposition="outside",
        textfont=dict(size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Tahun %{x}</b><br>ILOR: <b>%{y:.2f}</b><br>(%{customdata})<extra></extra>",
        customdata=["Jobless Growth" if v < 0 else "Penyerapan TK Positif" for v in _df_ilor["ilor"]],
        name="ILOR",
    ))
    fig.add_hline(y=0, line=dict(color=COLORS["gray_mid"], dash="dot", width=1.5))

    fig.update_layout(
        yaxis=dict(title="ILOR (jiwa / miliar Rp)"),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=55, r=25, t=40, b=50),
    )
    return fig


def _build_grafik_etk():
    """Bar chart ETK per tahun."""
    bar_colors = [
        COLORS["primary"] if v > 0 else COLORS["accent"]
        for v in _df_etk["etk"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_df_etk["tahun"].astype(str),
        y=_df_etk["etk"],
        marker_color=bar_colors,
        text=[f"{v:.2f}" for v in _df_etk["etk"]],
        textposition="outside",
        textfont=dict(size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Tahun %{x}</b><br>ETK: <b>%{y:.2f}</b><extra></extra>",
        name="ETK",
    ))
    fig.add_hline(y=0, line=dict(color=COLORS["gray_mid"], dash="dot", width=1.5))
    fig.add_hline(
        y=1,
        line=dict(color=COLORS["primary_light"], dash="dash", width=1.5),
        annotation_text="ETK = 1 (proporsional)",
        annotation_position="top right",
        annotation_font=dict(size=10, color=COLORS["primary_light"]),
    )

    fig.update_layout(
        yaxis=dict(title="Elastisitas Tenaga Kerja (ETK)"),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=55, r=25, t=40, b=50),
    )
    return fig


def _build_grafik_perubahan_pct():
    """Grouped bar chart % perubahan TK vs % perubahan PDRB."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_df_etk["tahun"].astype(str),
        y=_df_etk["pct_perubahan_tk"],
        name="% Δ TK",
        marker_color=COLORS["primary"],
        text=[f"{v:.2f}%" for v in _df_etk["pct_perubahan_tk"]],
        textposition="outside",
        hovertemplate="<b>Tahun %{x}</b><br>%ΔTK: %{y:.2f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=_df_etk["tahun"].astype(str),
        y=_df_etk["pct_perubahan_y"],
        name="% Δ PDRB",
        marker_color=COLORS["accent"],
        text=[f"{v:.2f}%" for v in _df_etk["pct_perubahan_y"]],
        textposition="outside",
        hovertemplate="<b>Tahun %{x}</b><br>%ΔPDRB: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=COLORS["gray_mid"], dash="dot", width=1.5))
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Perubahan (%)"),
        xaxis=dict(title="Tahun"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        margin=dict(l=55, r=25, t=50, b=50),
    )
    return fig


def _build_grafik_tk_pdrb():
    """Line chart tren Jumlah Penduduk Bekerja vs PDRB ADHK."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=_df_tk["tahun"].astype(str),
        y=_df_tk["jumlah_penduduk_bekerja"],
        name="Penduduk Bekerja (jiwa)",
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=9),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>TK: %{y:,.0f} jiwa<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=_df_tk["tahun"].astype(str),
        y=_df_tk["pdrb_adhk"],
        name="PDRB ADHK (miliar Rp)",
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2.5, dash="dot"),
        marker=dict(size=9, symbol="diamond"),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>PDRB: Rp %{y:,.2f} M<extra></extra>",
    ))
    fig.update_layout(
        yaxis=dict(title="Jumlah Penduduk Bekerja (jiwa)", tickformat=",.0f", side="left"),
        yaxis2=dict(title="PDRB ADHK (miliar Rp)", tickformat=",.0f", overlaying="y", side="right"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        margin=dict(l=65, r=65, t=50, b=50),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Layout Tab
# ---------------------------------------------------------------------------
def layout():
    tahun_etk_pos_str = ", ".join(str(t) for t in _etk_positif)

    return html.Div([
        # ── Hero Insight Card ───────────────────────────────────────────
        html.Div(
            style={
                "marginBottom": "22px",
                "padding": "20px 28px",
                "background": f"linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%)",
                "borderRadius": "14px",
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "center",
                "boxShadow": "0 4px 14px rgba(12, 32, 58, 0.12)",
            },
            children=[
                html.Img(
                    src="/assets/maskot_1.webp",
                    style={
                        "height": "120px", "width": "auto",
                        "objectFit": "contain", "flexShrink": "0",
                        "marginRight": "26px",
                        "filter": "drop-shadow(0 6px 14px rgba(0,0,0,0.3))",
                    },
                ),
                html.Div(
                    style={"flex": "1", "color": COLORS["white"]},
                    children=[
                        html.H3(
                            "Penyerapan Tenaga Kerja vs Pertumbuhan Ekonomi Kepri",
                            style={"fontSize": "18px", "fontWeight": "700", "margin": "0 0 8px 0", "color": COLORS["accent"]},
                        ),
                        html.P(
                            children=[
                                "Dari 5 tahun pengamatan (2021–2025), sebanyak ",
                                html.Strong(str(_n_negatif_ilor), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                " tahun mencatat ILOR negatif (jobless growth — PDRB tumbuh namun TK menyusut), "
                                "dan ",
                                html.Strong(str(_n_positif_ilor), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                " tahun mencatat ILOR positif (penyerapan TK beriringan dengan pertumbuhan). "
                                "ETK positif hanya pada tahun ",
                                html.Strong(tahun_etk_pos_str, style={"color": COLORS["accent"], "fontSize": "15px"}),
                                ", mencerminkan dominasi sektor padat modal di Kepri.",
                            ],
                            style={"fontSize": "13.5px", "lineHeight": "1.65", "margin": "0", "color": "rgba(255,255,255,0.9)"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Baris 1: ILOR & ETK ───────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("ILOR per Tahun (ILOR negatif = Jobless Growth)", className="card-title"),
                        dcc.Graph(id="graf-ilor-bar", figure=_build_grafik_ilor(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Elastisitas Tenaga Kerja (ETK) per Tahun", className="card-title"),
                        dcc.Graph(id="graf-etk-bar", figure=_build_grafik_etk(), style={"height": "360px"}),
                    ],
                ),
            ],
        ),

        # ── Baris 2: % Perubahan & Tren TK-PDRB ─────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("% Perubahan TK vs % Pertumbuhan PDRB", className="card-title"),
                        dcc.Graph(id="graf-ilor-pct", figure=_build_grafik_perubahan_pct(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Tren Jumlah Penduduk Bekerja & PDRB ADHK 2020–2025", className="card-title"),
                        dcc.Graph(id="graf-tk-pdrb", figure=_build_grafik_tk_pdrb(), style={"height": "360px"}),
                    ],
                ),
            ],
        ),

        # ── Tabel Detail ─────────────────────────────────────────────
        card(
            "Tabel Rekap ILOR & ETK — Kepulauan Riau 2021–2025",
            html.Div(
                style={"overflowX": "auto"},
                children=[
                    html.Table(
                        style={
                            "width": "100%", "borderCollapse": "collapse",
                            "fontSize": "13px", "fontFamily": "Inter, sans-serif",
                        },
                        children=[
                            html.Thead(
                                html.Tr([
                                    html.Th(h, style={
                                        "padding": "10px 14px", "textAlign": "center",
                                        "background": COLORS["primary"], "color": COLORS["white"],
                                        "fontWeight": "600", "whiteSpace": "nowrap",
                                    })
                                    for h in ["Tahun", "% ΔTK", "% ΔPDRB", "ILOR", "ETK", "Interpretasi"]
                                ])
                            ),
                            html.Tbody([
                                html.Tr(
                                    [
                                        html.Td(str(row["tahun"]), style={"padding": "9px 14px", "textAlign": "center", "fontWeight": "600", "color": COLORS["primary"]}),
                                        html.Td(
                                            f"{row['pct_perubahan_tk']:.2f}%",
                                            style={"padding": "9px 14px", "textAlign": "right",
                                                   "color": COLORS["primary"] if row["pct_perubahan_tk"] >= 0 else COLORS["accent"]}
                                        ),
                                        html.Td(f"{row['pct_perubahan_y']:.2f}%", style={"padding": "9px 14px", "textAlign": "right"}),
                                        html.Td(
                                            f"{_df_ilor[_df_ilor['tahun']==row['tahun']]['ilor'].values[0]:.2f}",
                                            style={"padding": "9px 14px", "textAlign": "center", "fontWeight": "700",
                                                   "color": COLORS["primary"] if _df_ilor[_df_ilor['tahun']==row['tahun']]['ilor'].values[0] > 0 else COLORS["accent"]}
                                        ),
                                        html.Td(
                                            f"{row['etk']:.2f}",
                                            style={"padding": "9px 14px", "textAlign": "center", "fontWeight": "700",
                                                   "color": COLORS["primary"] if row["etk"] > 0 else COLORS["accent"]}
                                        ),
                                        html.Td(
                                            "✅ TK Positif" if row["etk"] > 0 else "⚠️ Jobless Growth",
                                            style={"padding": "9px 14px", "textAlign": "center", "fontSize": "12px"}
                                        ),
                                    ],
                                    style={"borderBottom": f"1px solid {COLORS['gray_light']}", "background": COLORS["white"] if i % 2 == 0 else "#f8fafc"},
                                )
                                for i, (_, row) in enumerate(_df_etk.iterrows())
                            ]),
                        ],
                    ),
                ],
            ),
        ),
    ])
