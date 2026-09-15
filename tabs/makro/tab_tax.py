"""
Tab Tax Ratio — Provinsi Kepulauan Riau
Sumber data: data/ICOR-ILOR-RPI-TAX.xlsx, Sheet "Tax Ratio"

Tax Ratio = (Penerimaan Pajak + Penerimaan SDA) / PDRB ADHB × 100%
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

# Data yang sudah diekstrak dan divalidasi dari sheet Tax Ratio
_df = pd.DataFrame({
    "tahun":              [2019,    2020,    2021,    2022,    2023,    2024,    2025],
    "pdrb_adhb":          [267631.5, 254095.4, 275622.9, 308739.7, 331644.5, 352436.4, 381729.9],
    "penerimaan_pajak":   [1185.20,  1033.40,  1191.20,  1492.76,  1631.49,  1777.70,  1447.29],
    "penerimaan_sda":     [644.06,   262.84,   233.56,   531.38,   403.00,   128.02,   341.26],
})
_df["total_penerimaan"] = _df["penerimaan_pajak"] + _df["penerimaan_sda"]
_df["tax_ratio"]        = (_df["total_penerimaan"] / _df["pdrb_adhb"]) * 100

# Statistik ringkas
_tax_avg   = _df["tax_ratio"].mean()
_tax_max   = _df["tax_ratio"].max()
_tax_min   = _df["tax_ratio"].min()
_tahun_max = int(_df.loc[_df["tax_ratio"].idxmax(), "tahun"])
_tahun_min = int(_df.loc[_df["tax_ratio"].idxmin(), "tahun"])

# Hanya periode 2021-2025 untuk tren terkini
_df_terkini = _df[_df["tahun"] >= 2021].copy()


# ---------------------------------------------------------------------------
# 2. Builder Grafik
# ---------------------------------------------------------------------------
def _build_grafik_tax_ratio():
    """Line chart Tax Ratio 2019–2025."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=_df["tahun"].astype(str),
        y=_df["tax_ratio"],
        mode="lines+markers+text",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=10, color=COLORS["primary"]),
        text=[f"{v:.4f}%" for v in _df["tax_ratio"]],
        textposition="top center",
        textfont=dict(size=10, color=COLORS["primary_dark"]),
        fill="tozeroy",
        fillcolor="rgba(23, 58, 102, 0.10)",
        hovertemplate="<b>Tahun %{x}</b><br>Tax Ratio: <b>%{y:.4f}%</b><extra></extra>",
        name="Tax Ratio (%)",
    ))

    fig.add_hline(
        y=_tax_avg,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=1.8),
        annotation_text=f"Rata-rata: {_tax_avg:.4f}%",
        annotation_position="top right",
        annotation_font=dict(size=10, color=COLORS["accent_dark"]),
    )

    fig.update_layout(
        yaxis=dict(title="Tax Ratio (%)"),
        xaxis=dict(title="Tahun"),
        showlegend=False,
        margin=dict(l=55, r=30, t=40, b=50),
    )
    return fig


def _build_grafik_komponen():
    """Stacked bar chart Pajak vs SDA per tahun."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["penerimaan_pajak"],
        name="Penerimaan Pajak (miliar Rp)",
        marker_color=COLORS["primary"],
        hovertemplate="<b>Tahun %{x}</b><br>Pajak: Rp %{y:,.2f} M<extra></extra>",
        text=[f"Rp {v:,.0f}M" for v in _df["penerimaan_pajak"]],
        textposition="inside",
        textfont=dict(color="white", size=10),
    ))
    fig.add_trace(go.Bar(
        x=_df["tahun"].astype(str),
        y=_df["penerimaan_sda"],
        name="Penerimaan SDA (miliar Rp)",
        marker_color=COLORS["accent"],
        hovertemplate="<b>Tahun %{x}</b><br>SDA: Rp %{y:,.2f} M<extra></extra>",
        text=[f"Rp {v:,.0f}M" for v in _df["penerimaan_sda"]],
        textposition="inside",
        textfont=dict(color=COLORS["primary_dark"], size=10),
    ))

    fig.update_layout(
        barmode="stack",
        yaxis=dict(title="Penerimaan (miliar Rp)", tickformat=",.0f"),
        xaxis=dict(title="Tahun"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        margin=dict(l=65, r=25, t=50, b=50),
    )
    return fig


def _build_grafik_pdrb_adhb():
    """Line chart PDRB ADHB sebagai denominator tax ratio."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=_df["tahun"].astype(str),
        y=_df["pdrb_adhb"],
        mode="lines+markers",
        line=dict(color=COLORS["primary_light"], width=2.5),
        marker=dict(size=9),
        fill="tonexty",
        hovertemplate="<b>Tahun %{x}</b><br>PDRB ADHB: Rp %{y:,.2f} M<extra></extra>",
        name="PDRB ADHB",
    ))
    fig.update_layout(
        yaxis=dict(title="PDRB ADHB (miliar Rp)", tickformat=",.0f"),
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
                            "Tax Ratio Kepulauan Riau 2019–2025",
                            style={"fontSize": "18px", "fontWeight": "700", "margin": "0 0 8px 0", "color": COLORS["accent"]},
                        ),
                        html.P(
                            children=[
                                "Rata-rata tax ratio Kepri periode 2019–2025 sebesar ",
                                html.Strong(f"{_tax_avg:.4f}%", style={"color": COLORS["accent"], "fontSize": "16px"}),
                                ". Nilai tertinggi tercatat pada tahun ",
                                html.Strong(str(_tahun_max), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                f" ({_tax_max:.4f}%) dan terendah pada tahun ",
                                html.Strong(str(_tahun_min), style={"color": COLORS["accent"], "fontSize": "16px"}),
                                f" ({_tax_min:.4f}%). "
                                "Tax ratio yang rendah secara relatif menunjukkan ruang perbaikan kapasitas fiskal daerah melalui optimasi penerimaan pajak dan pengelolaan SDA.",
                            ],
                            style={"fontSize": "13.5px", "lineHeight": "1.65", "margin": "0", "color": "rgba(255,255,255,0.9)"},
                        ),
                    ],
                ),
            ],
        ),

        # ── Baris 1: Tax Ratio Line & Komponen Penerimaan ─────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Tren Tax Ratio Kepulauan Riau 2019–2025 (%)", className="card-title"),
                        dcc.Graph(id="graf-tax-line", figure=_build_grafik_tax_ratio(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Komponen Penerimaan: Pajak vs SDA (miliar Rp)", className="card-title"),
                        dcc.Graph(id="graf-tax-komponen", figure=_build_grafik_komponen(), style={"height": "360px"}),
                    ],
                ),
            ],
        ),

        # ── Baris 2: PDRB ADHB & Tabel ──────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("PDRB ADHB sebagai Basis Perhitungan Tax Ratio", className="card-title"),
                        dcc.Graph(id="graf-tax-pdrb", figure=_build_grafik_pdrb_adhb(), style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="card-box",
                    style={"flex": "1", "minWidth": "380px", "marginBottom": "0"},
                    children=[
                        html.Div("Tabel Detail Tax Ratio — Kepulauan Riau 2019–2025", className="card-title"),
                        html.Div(
                            style={"overflowX": "auto", "paddingTop": "8px"},
                            children=[
                                html.Table(
                                    style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px", "fontFamily": "Inter, sans-serif"},
                                    children=[
                                        html.Thead(
                                            html.Tr([
                                                html.Th(h, style={
                                                    "padding": "10px 10px", "textAlign": "center",
                                                    "background": COLORS["primary"], "color": COLORS["white"],
                                                    "fontWeight": "600", "whiteSpace": "nowrap",
                                                })
                                                for h in ["Tahun", "PDRB ADHB", "Pajak (M Rp)", "SDA (M Rp)", "Total", "Tax Ratio (%)"]
                                            ])
                                        ),
                                        html.Tbody([
                                            html.Tr(
                                                [
                                                    html.Td(str(row["tahun"]), style={"padding": "8px 10px", "textAlign": "center", "fontWeight": "600", "color": COLORS["primary"]}),
                                                    html.Td(f"{row['pdrb_adhb']:,.1f}", style={"padding": "8px 10px", "textAlign": "right"}),
                                                    html.Td(f"{row['penerimaan_pajak']:,.2f}", style={"padding": "8px 10px", "textAlign": "right"}),
                                                    html.Td(f"{row['penerimaan_sda']:,.2f}", style={"padding": "8px 10px", "textAlign": "right"}),
                                                    html.Td(f"{row['total_penerimaan']:,.2f}", style={"padding": "8px 10px", "textAlign": "right", "fontWeight": "600"}),
                                                    html.Td(
                                                        f"{row['tax_ratio']:.4f}%",
                                                        style={
                                                            "padding": "8px 10px", "textAlign": "center", "fontWeight": "700",
                                                            "color": COLORS["accent"] if row["tax_ratio"] == _tax_max else (
                                                                "#E76F51" if row["tax_ratio"] == _tax_min else COLORS["primary"]
                                                            ),
                                                        }
                                                    ),
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
