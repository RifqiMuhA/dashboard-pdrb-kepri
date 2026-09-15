"""
Tab RPI (Rasio Perdagangan Internasional) — Provinsi Kepulauan Riau
Sumber data: data/ICOR-ILOR-RPI-TAX.xlsx, Sheet "RASIO PERDAGANGAN INTERNASIONAL"

RPI = (X - M) / (X + M)
RPI > 0 : surplus perdagangan (eksportir neto)
RPI < 0 : defisit perdagangan (importir neto)
RPI = 0 : seimbang
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

# Data dari sheet RASIO PERDAGANGAN INTERNASIONAL
_df = pd.DataFrame({
    "tahun": [2021, 2022, 2023, 2024, 2025],
    "ekspor": [238160.04, 299323.00, 308884.07, 338661.01, 421812.05],
    "impor":  [212601.04, 260220.32, 281078.51, 281759.87, 372387.15],
})
_df["selisih"]  = _df["ekspor"] - _df["impor"]
_df["total"]    = _df["ekspor"] + _df["impor"]
_df["rpi"]      = _df["selisih"] / _df["total"]

# Statistik ringkas
_rpi_avg    = _df["rpi"].mean()
_rpi_max    = _df["rpi"].max()
_tahun_max  = int(_df.loc[_df["rpi"].idxmax(), "tahun"])
_surplus_avg = _df["selisih"].mean()


# ---------------------------------------------------------------------------
# 2. Builder Grafik
# ---------------------------------------------------------------------------
def _build_grafik_rpi():
    """Line + area chart RPI per tahun."""
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=_df["tahun"].astype(str),
        y=_df["rpi"],
        mode="lines+markers+text",
        fill="tozeroy",
        fillcolor="rgba(23, 58, 102, 0.12)",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=10, color=COLORS["primary"], symbol="circle"),
        text=[f"RPI = {v:.4f}" for v in _df["rpi"]],
        textposition="top center",
        textfont=dict(size=10, color=COLORS["primary_dark"]),
        hovertemplate=(
            "<b>Tahun %{x}</b><br>"
            "RPI: <b>%{y:.4f}</b><br>"
            "(%{customdata})<extra></extra>"
        ),
        customdata=["Surplus (X>M)" if v > 0 else "Defisit (M>X)" for v in _df["rpi"]],
        name="RPI",
    ))

    fig.add_hline(y=0, line=dict(color=COLORS["gray_mid"], dash="dot", width=1.5))
    fig.add_hline(
        y=_rpi_avg,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=1.8),
        annotation_text=f"Rata-rata: {_rpi_avg:.4f}",
        annotation_position="top right",
        annotation_font=dict(size=10, color=COLORS["accent_dark"]),
    )

    fig.update_layout(
        yaxis=dict(title="RPI (−1 s/d +1)", range=[-0.05, 0.20]),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=55, r=30, t=40, b=50),
    )
    return fig


def _build_grafik_xm():
    """Grouped bar chart Ekspor vs Impor per tahun."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["ekspor"],
        name="Ekspor (X)",
        marker_color=COLORS["primary"],
        text=[f"Rp {v/1000:,.1f} T" for v in _df["ekspor"]],
        textposition="outside",
        hovertemplate="<b>Tahun %{x}</b><br>Ekspor: Rp %{y:,.2f} M<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["impor"],
        name="Impor (M)",
        marker_color=COLORS["accent"],
        text=[f"Rp {v/1000:,.1f} T" for v in _df["impor"]],
        textposition="outside",
        hovertemplate="<b>Tahun %{x}</b><br>Impor: Rp %{y:,.2f} M<extra></extra>",
    ))

    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Nilai (miliar Rp ADHB)", tickformat=",.0f"),
        xaxis=dict(title="Tahun"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        margin=dict(l=65, r=25, t=50, b=50),
    )
    return fig


def _build_grafik_selisih():
    """Bar chart surplus/defisit perdagangan (X - M)."""
    bar_colors = [COLORS["primary"] if v > 0 else COLORS["accent"] for v in _df["selisih"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["selisih"],
        marker_color=bar_colors,
        text=[f"Rp {v:,.0f} M" for v in _df["selisih"]],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>Tahun %{x}</b><br>X − M: Rp %{y:,.2f} M<extra></extra>",
        name="Surplus / Defisit",
    ))
    fig.add_hline(y=0, line=dict(color=COLORS["gray_mid"], dash="dot", width=1.5))

    fig.update_layout(
        yaxis=dict(title="Surplus / Defisit (miliar Rp ADHB)", tickformat=",.0f"),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=65, r=25, t=40, b=50),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Layout Tab
# ---------------------------------------------------------------------------
def layout():
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
                            "Rasio Perdagangan Internasional (RPI) Kepulauan Riau",
                            style={"fontSize": "18px", "fontWeight": "700", "margin": "0 0 8px 0", "color": COLORS["accent"]},
                        ),
                        html.P(
                            children=[
                                "Selama 2021–2025, Kepulauan Riau konsisten mencatat ",
                                html.Strong("surplus perdagangan internasional", style={"color": COLORS["accent"]}),
                                " (RPI > 0). RPI rata-rata sebesar ",
                                html.Strong(f"{_rpi_avg:.4f}", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                ", dengan surplus tertinggi pada tahun ",
                                html.Strong(str(_tahun_max), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                f" (RPI = {_rpi_max:.4f}). Rata-rata surplus X − M mencapai ",
                                html.Strong(f"Rp {_surplus_avg:,.0f} miliar", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                " per tahun, menjadikan Kepri sebagai eksportir neto yang kuat di kawasan.",
                            ],
                            style={"fontSize": "13.5px", "lineHeight": "1.65", "margin": "0", "color": "rgba(255,255,255,0.9)"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Baris 1: RPI Line Chart & X vs M Bar ────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Tren Rasio Perdagangan Internasional (RPI) 2021–2025", className="card-title"),
                        dcc.Graph(id="graf-rpi-line", figure=_build_grafik_rpi(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Nilai Ekspor (X) vs Impor (M) ADHB — miliar Rp", className="card-title"),
                        dcc.Graph(id="graf-rpi-xm", figure=_build_grafik_xm(), style={"height": "360px"}),
                    ],
                ),
            ],
        ),

        # ── Baris 2: Surplus/Defisit & Tabel ─────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Surplus / Defisit Perdagangan (X − M)", className="card-title"),
                        dcc.Graph(id="graf-rpi-selisih", figure=_build_grafik_selisih(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Tabel Detail RPI — Kepulauan Riau 2021–2025", className="card-title"),
                        html.Div(
                            style={"overflowX": "auto", "paddingTop": "8px"},
                            children=[
                                html.Table(
                                    style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px", "fontFamily": "Inter, sans-serif"},
                                    children=[
                                        html.Thead(
                                            html.Tr([
                                                html.Th(h, style={
                                                    "padding": "10px 12px", "textAlign": "center",
                                                    "background": COLORS["primary"], "color": COLORS["white"],
                                                    "fontWeight": "600", "whiteSpace": "nowrap",
                                                })
                                                for h in ["Tahun", "Ekspor X (M Rp)", "Impor M (M Rp)", "X−M (M Rp)", "X+M (M Rp)", "RPI"]
                                            ])
                                        ),
                                        html.Tbody([
                                            html.Tr(
                                                [
                                                    html.Td(str(row["tahun"]), style={"padding": "9px 12px", "textAlign": "center", "fontWeight": "600", "color": COLORS["primary"]}),
                                                    html.Td(f"{row['ekspor']:,.2f}", style={"padding": "9px 12px", "textAlign": "right"}),
                                                    html.Td(f"{row['impor']:,.2f}", style={"padding": "9px 12px", "textAlign": "right"}),
                                                    html.Td(f"{row['selisih']:,.2f}", style={"padding": "9px 12px", "textAlign": "right", "color": COLORS["primary"], "fontWeight": "600"}),
                                                    html.Td(f"{row['total']:,.2f}", style={"padding": "9px 12px", "textAlign": "right"}),
                                                    html.Td(f"{row['rpi']:.4f}", style={"padding": "9px 12px", "textAlign": "center", "fontWeight": "700",
                                                                                         "color": COLORS["primary"] if row["rpi"] > _rpi_avg else COLORS["accent_dark"]}),
                                                ],
                                                style={"borderBottom": f"1px solid {COLORS['gray_light']}", "background": COLORS["white"] if i % 2 == 0 else "#f8fafc"},
                                            )
                                            for i, (_, row) in enumerate(_df.iterrows())
                                        ]),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ])
