"""
Tab Konsumsi Rumah Tangga: APC, APS, MPC, dan MPS — Provinsi Kepulauan Riau
Sumber data: data/APC_MPC_Kepri_2021-2025.xlsx
  - Sheet "APC-MPC Kepri" : Data Pendapatan (Yd), Konsumsi (C), APC, dan APS
  - Sheet "Sheet1"        : Data Delta C, Delta Yd, MPC, dan MPS
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.components import card
from theme import COLORS

# ---------------------------------------------------------------------------
# 1. Load Data
# ---------------------------------------------------------------------------
_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "APC_MPC_Kepri_2021-2025.xlsx"
_xl = pd.ExcelFile(_DATA_PATH)

_df_apc = _xl.parse("APC-MPC Kepri")
_df_mpc = _xl.parse("Sheet1")

# Standardisasi nama kolom agar mudah diakses
_df_apc.columns = ["tahun", "yd", "c", "apc", "aps"]
_df_mpc.columns = ["periode", "delta_c", "delta_yd", "mpc", "mps"]

_df_apc["tahun"] = _df_apc["tahun"].astype(int)

# Metrik Rangkuman
_avg_apc = _df_apc["apc"].mean() * 100
_avg_aps = _df_apc["aps"].mean() * 100
_avg_mpc = _df_mpc["mpc"].mean()
_avg_mps = _df_mpc["mps"].mean()
_multiplier = 1.0 / (1.0 - _avg_mpc) if (1.0 - _avg_mpc) != 0 else 0.0

# Regresi Fungsi Konsumsi Keynesian: C = a + b * Yd
_x_val = _df_apc["yd"].values
_y_val = _df_apc["c"].values
_slope, _intercept = np.polyfit(_x_val, _y_val, 1)
_r2 = np.corrcoef(_x_val, _y_val)[0, 1] ** 2


# ---------------------------------------------------------------------------
# 2. Builder Grafik
# ---------------------------------------------------------------------------
def _build_grafik_apc_aps(unit: str = "persen"):
    """Grafik Komposisi Proporsi APC dan APS (Konsumsi vs Tabungan)"""
    fig = go.Figure()

    multiplier = 100.0 if unit == "persen" else 1.0
    suffix = "%" if unit == "persen" else ""
    y_max = 105.0 if unit == "persen" else 1.05

    fig.add_trace(go.Bar(
        x=_df_apc["tahun"].astype(str),
        y=_df_apc["apc"] * multiplier,
        name="APC (Konsumsi RT)",
        marker_color=COLORS["primary"],
        text=[f"{v * multiplier:.2f}{suffix}" for v in _df_apc["apc"]],
        textposition="inside",
        textfont=dict(color="white", size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Tahun %{x}</b><br>APC: %{y:.2f}" + suffix + "<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=_df_apc["tahun"].astype(str),
        y=_df_apc["aps"] * multiplier,
        name="APS (Tabungan / Surplus)",
        marker_color=COLORS["accent"],
        text=[f"{v * multiplier:.2f}{suffix}" for v in _df_apc["aps"]],
        textposition="inside",
        textfont=dict(color=COLORS["primary_dark"], size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Tahun %{x}</b><br>APS: %{y:.2f}" + suffix + "<extra></extra>",
    ))

    fig.update_layout(
        barmode="stack",
        yaxis=dict(title=f"Proporsi ({'%' if unit == 'persen' else 'Rasio'})", range=[0, y_max]),
        xaxis=dict(title="Tahun"),
        margin=dict(l=50, r=20, t=30, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )
    return fig


def _build_grafik_mpc_mps():
    """Grafik Kecenderungan Marjinal MPC dan MPS Antar-Periode"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=_df_mpc["periode"],
        y=_df_mpc["mpc"],
        name="MPC (Marginal Konsumsi)",
        marker_color=COLORS["primary"],  # Biru Utama Dashboard
        text=[f"{v:.4f}" for v in _df_mpc["mpc"]],
        textposition="outside",
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate="<b>Periode %{x}</b><br>MPC: %{y:.4f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=_df_mpc["periode"],
        y=_df_mpc["mps"],
        name="MPS (Marginal Tabungan)",
        marker_color=COLORS["accent"],  # Kuning-Oranye Aksen Dashboard
        text=[f"{v:.4f}" for v in _df_mpc["mps"]],
        textposition="outside",
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate="<b>Periode %{x}</b><br>MPS: %{y:.4f}<extra></extra>",
    ))

    # Garis rata-rata MPC
    fig.add_hline(
        y=_avg_mpc,
        line=dict(color=COLORS["primary_light"], dash="dash", width=1.5),
        annotation_text=f"Rata-rata MPC: {_avg_mpc:.3f}",
        annotation_position="top left",
        annotation_font=dict(size=10, color=COLORS["primary"]),
    )

    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Nilai Marjinal (0 - 1)", range=[0, 0.75]),
        xaxis=dict(title="Periode Perubahan"),
        margin=dict(l=50, r=20, t=30, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )
    return fig


def _build_grafik_fungsi_konsumsi():
    """Grafik Garis Regresi Fungsi Konsumsi Keynesian: C = f(Yd)"""
    fig = go.Figure()

    # Titik observasi per tahun
    fig.add_trace(go.Scatter(
        x=_df_apc["yd"],
        y=_df_apc["c"],
        mode="markers+text",
        text=[f"  {t}" for t in _df_apc["tahun"]],
        textposition="top left",
        marker=dict(size=11, color=COLORS["primary"], symbol="circle"),
        name="Data Aktual (2021-2025)",
        hovertemplate="<b>Tahun:</b> %{text}<br><b>Yd:</b> Rp %{x:,.2f} M<br><b>C:</b> Rp %{y:,.2f} M<extra></extra>",
    ))

    # Garis tren regresi
    x_trend = np.linspace(_df_apc["yd"].min() * 0.98, _df_apc["yd"].max() * 1.02, 50)
    y_trend = _intercept + _slope * x_trend

    tanda = "+" if _intercept >= 0 else "-"
    intercept_abs = abs(_intercept)
    persamaan_text = f"C = {_slope:.4f}·Yd {tanda} {intercept_abs:,.0f} (R² = {_r2:.4f})"

    fig.add_trace(go.Scatter(
        x=x_trend,
        y=y_trend,
        mode="lines",
        line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
        name=f"Garis Fungsi Konsumsi: {persamaan_text}",
    ))

    fig.update_layout(
        xaxis=dict(title="Pendapatan / PDRB (Yd) — Miliar Rp", tickformat=",.0f"),
        yaxis=dict(title="Pengeluaran Konsumsi RT (C) — Miliar Rp", tickformat=",.0f"),
        margin=dict(l=65, r=25, t=30, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Layout Tab
# ---------------------------------------------------------------------------
def layout():
    return html.Div([
        # ── Hero Insight Card dengan Maskot di Sisi Kiri ─────────────────────
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
                # Gambar Maskot di Sisi Kiri
                html.Img(
                    src="/assets/maskot_1.webp",
                    style={
                        "height": "125px",
                        "width": "auto",
                        "objectFit": "contain",
                        "flexShrink": "0",
                        "marginRight": "26px",
                        "filter": "drop-shadow(0 6px 14px rgba(0,0,0,0.3))",
                    },
                ),
                # Narasi Insight di Sisi Kanan
                html.Div(
                    style={"flex": "1", "color": COLORS["white"]},
                    children=[
                        html.H3(
                            "Karakteristik Konsumsi Rumah Tangga & Daya Pengganda Ekonomi",
                            style={"fontSize": "19px", "fontWeight": "700", "margin": "0 0 8px 0", "color": COLORS["accent"]},
                        ),
                        html.P(
                            children=[
                                "Sepanjang 2021–2025, rata-rata pengeluaran konsumsi rumah tangga Kepri menyerap ",
                                html.Strong(f"{_avg_apc:.2f}%", style={"color": COLORS["accent"], "fontSize": "16px", "fontWeight": "700"}),
                                " dari total PDRB (APC), dengan sisa ",
                                html.Strong(f"{_avg_aps:.2f}%", style={"color": "#FFFFFF", "fontSize": "16px", "fontWeight": "700"}),
                                " berupa tabungan dan investasi (APS). Secara marjinal, setiap pertambahan pendapatan sebesar Rp 1.000 mendorong konsumsi baru sebesar ",
                                html.Strong(f"Rp {_avg_mpc*1000:,.0f}", style={"color": COLORS["accent"], "fontSize": "16px", "fontWeight": "700"}),
                                " (MPC = ",
                                html.Strong(f"{_avg_mpc:.4f}", style={"color": COLORS["accent"], "fontSize": "16px", "fontWeight": "700"}),
                                "), yang menghasilkan daya dorong pengganda ekonomi (",
                                html.Em("multiplier"),
                                ") sebesar ",
                                html.Strong(f"{_multiplier:.2f}x", style={"color": COLORS["accent"], "fontSize": "17px", "fontWeight": "700"}),
                                " bagi perekonomian Kepulauan Riau.",
                            ],
                            style={"fontSize": "13.5px", "lineHeight": "1.65", "margin": "0", "color": "rgba(255, 255, 255, 0.9)"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Kontrol Pilihan Satuan / Tampilan ───────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"minWidth": "220px"},
                    children=[
                        html.Label("Satuan Proporsi APC/APS", className="filter-label"),
                        dcc.RadioItems(
                            id="apc-unit-selector",
                            options=[
                                {"label": " Persentase (%)", "value": "persen"},
                                {"label": " Rasio (0 - 1)", "value": "rasio"},
                            ],
                            value="persen",
                            inline=True,
                            style={"display": "flex", "gap": "14px", "alignItems": "center", "height": "36px", "fontSize": "13px"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Baris 1: Grafik APC/APS & Grafik MPC/MPS ────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                # Kartu APC & APS
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "420px", "marginBottom": "0"},
                    children=[
                        html.Div("Proporsi Konsumsi (APC) vs Tabungan (APS) per Tahun", className="card-title"),
                        dcc.Graph(id="graf-apc-aps", style={"height": "380px"}),
                    ],
                ),
                # Kartu MPC & MPS
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "420px", "marginBottom": "0"},
                    children=[
                        html.Div("Kecenderungan Marjinal: MPC vs MPS per Periode", className="card-title"),
                        dcc.Graph(id="graf-mpc-mps", figure=_build_grafik_mpc_mps(), style={"height": "380px"}),
                    ],
                ),
            ],
        ),

        # ── Baris 2: Kurva Fungsi Konsumsi Keynesian ────────────────────────
        card(
            "Fungsi Konsumsi Keynesian: Konsumsi Rumah Tangga (C) vs PDRB (Yd)",
            dcc.Graph(id="graf-fungsi-konsumsi", figure=_build_grafik_fungsi_konsumsi(), style={"height": "400px"}),
        ),
    ])


# ---------------------------------------------------------------------------
# 5. Callbacks
# ---------------------------------------------------------------------------
@callback(
    Output("graf-apc-aps", "figure"),
    Input("apc-unit-selector", "value"),
)
def update_grafik_apc(unit):
    return _build_grafik_apc_aps(unit or "persen")
