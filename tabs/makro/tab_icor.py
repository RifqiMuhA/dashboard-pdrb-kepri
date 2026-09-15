"""
Tab ICOR (Incremental Capital-Output Ratio) — Provinsi Kepulauan Riau
Sumber data: data/ICOR-ILOR-RPI-TAX.xlsx, Sheet "ICOR"

ICOR = PMTB (ADHK) / Delta PDRB (ADHK)
Nilai lebih rendah → investasi lebih efisien menghasilkan output baru.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.components import card, mascot_insight_bubble
from theme import COLORS

# ---------------------------------------------------------------------------
# 1. Load Data dari Excel
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ICOR-ILOR-RPI-TAX.xlsx"
_xl = pd.ExcelFile(_DATA_PATH)
_raw = _xl.parse("ICOR")

# Ambil tabel ringkas di kolom Unnamed: 8 (Tahun) dan Unnamed: 9 (ICOR)
_df = pd.DataFrame({
    "tahun": [2021, 2022, 2023, 2024, 2025],
    "icor":  [12.02, 8.19, 8.31, 8.64, 6.35],
})

# Tabel detail
_df_detail = pd.DataFrame({
    "tahun":    [2021, 2022, 2023, 2024, 2025],
    "pdrb_adhk": [180952.44, 190111.09, 199912.83, 209939.07, 224504.72],
    "delta_pdrb": [5993.24, 9158.64, 9801.74, 10026.25, 14565.65],
    "pmtb_adhk":  [72042.69, 74944.81, 81476.94, 86579.47, 92478.32],
    "icor":      [12.02, 8.19, 8.31, 8.64, 6.35],
})

# Statistik ringkas
_icor_avg   = _df["icor"].mean()
_icor_min   = _df["icor"].min()
_icor_max   = _df["icor"].max()
_tahun_min  = int(_df.loc[_df["icor"].idxmin(), "tahun"])


# ---------------------------------------------------------------------------
# 2. Builder Grafik
# ---------------------------------------------------------------------------
def _build_grafik_icor():
    """Bar chart ICOR per tahun + garis rata-rata."""
    bar_colors = [
        COLORS["accent"] if v == _icor_min else COLORS["primary"]
        for v in _df["icor"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["icor"],
        marker_color=bar_colors,
        text=[f"{v:.2f}" for v in _df["icor"]],
        textposition="outside",
        textfont=dict(size=12, family="Inter, sans-serif", color=COLORS["gray_dark"]),
        hovertemplate="<b>Tahun %{x}</b><br>ICOR: <b>%{y:.2f}</b><extra></extra>",
        name="ICOR",
    ))

    # Garis rata-rata
    fig.add_hline(
        y=_icor_avg,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=1.8),
        annotation_text=f"Rata-rata: {_icor_avg:.2f}",
        annotation_position="top right",
        annotation_font=dict(size=10, color=COLORS["accent_dark"]),
    )

    fig.update_layout(
        yaxis=dict(
            title="Nilai ICOR",
            rangemode="tozero",
        ),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=50, r=30, t=40, b=50),
    )
    return fig


def _build_grafik_komponen():
    """Line chart komponen PMTB dan Delta PDRB (ADHK)."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=_df_detail["tahun"].astype(str),
        y=_df_detail["pmtb_adhk"],
        name="PMTB (ADHK, miliar Rp)",
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=9, symbol="circle"),
        hovertemplate="<b>%{x}</b><br>PMTB: Rp %{y:,.2f} M<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=_df_detail["tahun"].astype(str),
        y=_df_detail["delta_pdrb"],
        name="ΔY PDRB (ADHK, miliar Rp)",
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2.5, dash="dot"),
        marker=dict(size=9, symbol="diamond"),
        hovertemplate="<b>%{x}</b><br>ΔPDRB: Rp %{y:,.2f} M<extra></extra>",
    ))

    fig.update_layout(
        yaxis=dict(title="Miliar Rupiah (ADHK 2010)", tickformat=",.0f"),
        xaxis=dict(title="Tahun"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=11),
        ),
        margin=dict(l=65, r=25, t=40, b=50),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Layout Tab
# ---------------------------------------------------------------------------
def layout():
    return html.Div([
        # ── Hero Insight Card ──────────────────────────────────────────────
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
                        "height": "120px",
                        "width": "auto",
                        "objectFit": "contain",
                        "flexShrink": "0",
                        "marginRight": "26px",
                        "filter": "drop-shadow(0 6px 14px rgba(0,0,0,0.3))",
                    },
                ),
                html.Div(
                    style={"flex": "1", "color": COLORS["white"]},
                    children=[
                        html.H3(
                            "Efisiensi Investasi Modal Kepulauan Riau (ICOR)",
                            style={"fontSize": "18px", "fontWeight": "700", "margin": "0 0 8px 0", "color": COLORS["accent"]},
                        ),
                        html.P(
                            children=[
                                "Nilai ICOR rata-rata 2021–2025 sebesar ",
                                html.Strong(f"{_icor_avg:.2f}", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                ". Nilai terbaik (efisiensi tertinggi) tercatat pada tahun ",
                                html.Strong(str(_tahun_min), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                " dengan ICOR ",
                                html.Strong(f"{_icor_min:.2f}", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                ", menunjukkan bahwa setiap tambahan Rp 1 output PDRB hanya membutuhkan investasi modal sebesar ",
                                html.Strong(f"Rp {_icor_min:.2f}", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                ". Tren menurun mengindikasikan investasi di Kepri semakin produktif.",
                            ],
                            style={"fontSize": "13.5px", "lineHeight": "1.65", "margin": "0", "color": "rgba(255,255,255,0.9)"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Baris Grafik ────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("ICOR per Tahun", className="card-title"),
                        dcc.Graph(
                            id="graf-icor-bar",
                            figure=_build_grafik_icor(),
                            style={"height": "380px"},
                        ),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Komponen ICOR: PMTB vs Pertambahan PDRB (ADHK)", className="card-title"),
                        dcc.Graph(
                            id="graf-icor-komponen",
                            figure=_build_grafik_komponen(),
                            style={"height": "380px"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Tabel Detail ─────────────────────────────────────────────────
        card(
            "Tabel Detail Perhitungan ICOR — Kepulauan Riau 2021–2025",
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
                                    for h in ["Tahun", "PDRB ADHK (miliar Rp)", "ΔPDRB (miliar Rp)", "PMTB ADHK (miliar Rp)", "ICOR"]
                                ])
                            ),
                            html.Tbody([
                                html.Tr(
                                    [
                                        html.Td(str(row["tahun"]), style={"padding": "9px 14px", "textAlign": "center", "fontWeight": "600", "color": COLORS["primary"]}),
                                        html.Td(f"{row['pdrb_adhk']:,.2f}", style={"padding": "9px 14px", "textAlign": "right"}),
                                        html.Td(f"{row['delta_pdrb']:,.2f}", style={"padding": "9px 14px", "textAlign": "right"}),
                                        html.Td(f"{row['pmtb_adhk']:,.2f}", style={"padding": "9px 14px", "textAlign": "right"}),
                                        html.Td(
                                            f"{row['icor']:.2f}",
                                            style={
                                                "padding": "9px 14px", "textAlign": "center",
                                                "fontWeight": "700",
                                                "color": COLORS["accent"] if row["icor"] == _icor_min else COLORS["gray_dark"],
                                            }
                                        ),
                                    ],
                                    style={"borderBottom": f"1px solid {COLORS['gray_light']}", "background": COLORS["white"] if i % 2 == 0 else "#f8fafc"},
                                )
                                for i, (_, row) in enumerate(_df_detail.iterrows())
                            ]),
                        ],
                    )
                ],
            ),
        ),
    ])
