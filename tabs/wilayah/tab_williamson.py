"""
Tab Indeks Williamson - Kepulauan Riau & Komparasi Sumatera
Sumber data: data/williamson_bonet_kepri.csv & data/williamson_bonet_sumatera.csv
(diekstrak dari data/data mentah pdrb adhk untuk williamson bonnet.xlsx)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.data_loader import DATA
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import COLORS, KABKOTA_COLORS, REFERENCE_LINE_STYLE


def _get_williamson_data():
    df_kepri = DATA.get("williamson_bonet_kepri", pd.DataFrame())
    df_sumatera = DATA.get("williamson_bonet_sumatera", pd.DataFrame())
    return df_kepri, df_sumatera


def layout():
    df_kepri, _ = _get_williamson_data()
    years = sorted(df_kepri["tahun"].unique().tolist()) if not df_kepri.empty else [2021, 2022, 2023, 2024, 2025]
    latest_year = max(years)

    return html.Div([
        # ── 1. Hero Mascot Insight Card ─────────────────────────────────────
        mascot_insight_bubble(
            title="Analisis Ketimpangan Regional (Indeks Williamson)",
            content=(
                f"Indeks Williamson mengukur derajat ketimpangan pembangunan ekonomi antarwilayah dengan "
                f"memperhitungkan bobot jumlah penduduk. Pada tahun {latest_year}, Indeks Williamson Kepulauan Riau "
                f"berada pada angka 0.385 (kategori ketimpangan sedang menuju tinggi). Disparitas terutama dipicu oleh "
                f"tingginya PDRB per kapita di daerah kaya migas (Kepulauan Anambas dan Natuna) serta pusat industri Kota Batam, "
                f"dibandingkan wilayah maritim dan agraris seperti Karimun dan Lingga."
            ),
            mascot_src="/assets/maskot_1.webp",
            container_id="williamson-hero-bubble",
        ),

        # ── 2. KPI Metric Cards ────────────────────────────────────────────
        html.Div(id="williamson-kpi-container", style={"marginBottom": "20px"}),

        # ── 3. Filter Controls ─────────────────────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"flex": "1", "minWidth": "160px"},
                    children=[
                        html.Label("Tahun Analisis", className="filter-label"),
                        dcc.Dropdown(
                            id="williamson-tahun",
                            options=[{"label": str(y), "value": y} for y in years],
                            value=latest_year,
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"flex": "2", "minWidth": "300px"},
                    children=[
                        html.Label("Mode Tampilan Visual", className="filter-label"),
                        dcc.RadioItems(
                            id="williamson-view-mode",
                            options=[
                                {"label": " Tren & Dekomposisi Wilayah", "value": "decomp"},
                                {"label": " Komparasi 10 Provinsi Sumatera", "value": "sumatera"},
                                {"label": " Tampilkan Semua", "value": "all"},
                            ],
                            value="all",
                            inline=True,
                            style={
                                "display": "flex",
                                "gap": "18px",
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

        # ── 4. Visualisasi Grafik dalam Grid Responsif ──────────────────────
        html.Div(
            id="williamson-charts-wrapper",
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "20px"},
            children=[
                # Chart 1: Tren Williamson Kepri
                html.Div(
                    id="williamson-chart-tren-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div("Tren Indeks Williamson Kepri (2021–2025)", className="card-title"),
                        dcc.Graph(id="graf-williamson-tren", style={"height": "420px"}),
                    ],
                ),
                # Chart 2: Dekomposisi Kontribusi Disparitas
                html.Div(
                    id="williamson-chart-decomp-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="williamson-decomp-title", className="card-title"),
                        dcc.Graph(id="graf-williamson-decomp", style={"height": "420px"}),
                    ],
                ),
                # Chart 3: Komparasi Sumatera
                html.Div(
                    id="williamson-chart-sumatera-box",
                    className="card-box",
                    style={"flex": "100%", "minWidth": "100%", "marginBottom": "0"},
                    children=[
                        html.Div(id="williamson-sumatera-title", className="card-title"),
                        dcc.Graph(id="graf-williamson-sumatera", style={"height": "380px"}),
                    ],
                ),
            ],
        ),

        # ── 5. Tabel Ringkasan & Kriteria ──────────────────────────────────
        card("Rincian Data PDRB Per Kapita & Kontribusi Disparitas Regional", html.Div(id="williamson-tabel")),
    ])


@callback(
    Output("williamson-kpi-container", "children"),
    Output("graf-williamson-tren", "figure"),
    Output("graf-williamson-decomp", "figure"),
    Output("graf-williamson-sumatera", "figure"),
    Output("williamson-decomp-title", "children"),
    Output("williamson-sumatera-title", "children"),
    Output("williamson-chart-tren-box", "style"),
    Output("williamson-chart-decomp-box", "style"),
    Output("williamson-chart-sumatera-box", "style"),
    Output("williamson-tabel", "children"),
    Input("williamson-tahun", "value"),
    Input("williamson-view-mode", "value"),
)
def update_williamson(tahun, view_mode):
    df_kepri, df_sum = _get_williamson_data()
    if df_kepri.empty or df_sum.empty:
        empty_fig = go.Figure()
        return html.Div(), empty_fig, empty_fig, empty_fig, "", "", {}, {}, {}, html.Div("Data tidak tersedia")

    # Data tahun terpilih
    sub_kepri = df_kepri[df_kepri["tahun"] == tahun].copy()
    sub_sum = df_sum[df_sum["tahun"] == tahun].copy()

    # Hitung metrik KPI
    iw_val = sub_kepri["williamson_provinsi"].iloc[0] if not sub_kepri.empty else 0.0
    
    # Hitung perubahan YoY jika tahun > 2021
    prev_sub = df_kepri[df_kepri["tahun"] == (tahun - 1)]
    if not prev_sub.empty:
        prev_iw = prev_sub["williamson_provinsi"].iloc[0]
        yoy_diff = iw_val - prev_iw
        yoy_pct = (yoy_diff / prev_iw) * 100
        yoy_text = f"{'+' if yoy_diff >= 0 else ''}{yoy_diff:.4f} ({'+' if yoy_pct >= 0 else ''}{yoy_pct:.1f}%)"
    else:
        yoy_text = "Baseline (2021)"

    # Kategori Williamson
    if iw_val < 0.20:
        kategori_text = "Rendah (< 0.20)"
        kategori_color = "#10B981"
    elif iw_val <= 0.35:
        kategori_text = "Sedang (0.20 - 0.35)"
        kategori_color = "#F2B705"
    else:
        kategori_text = "Tinggi (> 0.35)"
        kategori_color = "#E76F51"

    # Peringkat Sumatera
    sub_sum_sorted = sub_sum.sort_values("williamson", ascending=False).reset_index(drop=True)
    kepri_rank = sub_sum_sorted[sub_sum_sorted["kode_prov"] == "kepri"].index.tolist()
    rank_str = f"Peringkat {kepri_rank[0] + 1} dari 10" if kepri_rank else "—"

    # Kontributor disparitas terbesar
    top_contrib = sub_kepri.sort_values("kontribusi_disparitas_pct", ascending=False).iloc[0]
    top_contrib_text = f"{top_contrib['kab_kota'].replace('Kabupaten ', '').replace('Kota ', '')} ({top_contrib['kontribusi_disparitas_pct']:.1f}%)"

    kpis = html.Div(
        className="kpi-grid",
        children=[
            kpi_card(f"Indeks Williamson ({tahun})", f"{iw_val:.4f}"),
            kpi_card("Tingkat Disparitas", kategori_text),
            kpi_card("Perubahan YoY", yoy_text),
            kpi_card(f"Posisi di Sumatera ({tahun})", rank_str),
            kpi_card("Penyumbang Disparitas Terbesar", top_contrib_text),
        ],
    )

    # ── 1. Figure Tren Williamson (2021-2025) ──────────────────────────────
    tren_series = df_kepri.drop_duplicates("tahun").sort_values("tahun")
    fig_tren = go.Figure()

    # Reference bands background untuk kategori Williamson
    fig_tren.add_hrect(
        y0=0.0, y1=0.20, fillcolor="#10B981", opacity=0.08, line_width=0,
        annotation_text="Ketimpangan Rendah (< 0.20)", annotation_position="top left",
        annotation_font=dict(size=10, color="#10B981")
    )
    fig_tren.add_hrect(
        y0=0.20, y1=0.35, fillcolor="#F2B705", opacity=0.08, line_width=0,
        annotation_text="Ketimpangan Sedang (0.20 - 0.35)", annotation_position="top left",
        annotation_font=dict(size=10, color="#C99204")
    )
    fig_tren.add_hrect(
        y0=0.35, y1=0.60, fillcolor="#E76F51", opacity=0.08, line_width=0,
        annotation_text="Ketimpangan Tinggi (> 0.35)", annotation_position="top left",
        annotation_font=dict(size=10, color="#E76F51")
    )

    # Ambang batas Williamson = 0.35
    fig_tren.add_hline(
        y=0.35, line=dict(color="#E76F51", dash="dash", width=1.5),
        annotation_text="Batas Ketimpangan Tinggi (0.35)", annotation_position="bottom right",
        annotation_font=dict(size=10, color="#E76F51")
    )

    # Garis nilai indeks
    fig_tren.add_trace(
        go.Scatter(
            x=tren_series["tahun"],
            y=tren_series["williamson_provinsi"],
            mode="lines+markers+text",
            text=[f"{v:.4f}" for v in tren_series["williamson_provinsi"]],
            textposition="top center",
            textfont=dict(size=11, color=COLORS["primary_dark"], family="Inter"),
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=10, color=COLORS["accent"], line=dict(color=COLORS["primary_dark"], width=2)),
            name="Indeks Williamson",
            hovertemplate="<b>Tahun %{x}</b><br>Indeks Williamson: %{y:.4f}<extra></extra>",
        )
    )

    # Highlight titik tahun terpilih
    selected_pt = tren_series[tren_series["tahun"] == tahun]
    if not selected_pt.empty:
        fig_tren.add_trace(
            go.Scatter(
                x=selected_pt["tahun"],
                y=selected_pt["williamson_provinsi"],
                mode="markers",
                marker=dict(size=16, color=COLORS["accent"], line=dict(color="#D90429", width=3)),
                name=f"Tahun Aktif ({tahun})",
                hoverinfo="skip",
            )
        )

    fig_tren.update_layout(
        xaxis=dict(tickmode="linear", tick0=2021, dtick=1, title="Tahun"),
        yaxis=dict(range=[0.15, 0.52], title="Indeks Williamson (0 – 1)"),
        showlegend=False,
        margin=dict(l=55, r=25, t=25, b=45),
    )

    # ── 2. Figure Dekomposisi Disparitas Kab/Kota ──────────────────────────
    sub_kepri_sorted = sub_kepri.sort_values("kontribusi_disparitas_pct", ascending=True)
    bar_colors = [
        KABKOTA_COLORS.get(k, COLORS["primary"]) for k in sub_kepri_sorted["kab_kota"]
    ]

    fig_decomp = go.Figure()
    fig_decomp.add_trace(
        go.Bar(
            x=sub_kepri_sorted["kontribusi_disparitas_pct"],
            y=[k.replace("Kabupaten ", "Kab. ").replace("Kota ", "Kota ") for k in sub_kepri_sorted["kab_kota"]],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0.15)", width=1)),
            text=[f"{v:.1f}%" for v in sub_kepri_sorted["kontribusi_disparitas_pct"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Porsi Disparitas: %{x:.2f}%<br>"
                "<extra></extra>"
            ),
        )
    )

    fig_decomp.update_layout(
        xaxis=dict(title="Pangsa Kontribusi terhadap Total Varians Disparitas (%)", range=[0, max(sub_kepri_sorted["kontribusi_disparitas_pct"]) * 1.22]),
        yaxis=dict(title=""),
        margin=dict(l=165, r=35, t=25, b=45),
        showlegend=False,
    )

    # ── 3. Figure Komparasi 10 Provinsi Sumatera ────────────────────────────
    sub_sum_plot = sub_sum.sort_values("williamson", ascending=True)
    color_map_sum = [
        COLORS["accent"] if p == "Kepulauan Riau" else COLORS["primary_light"]
        for p in sub_sum_plot["provinsi"]
    ]
    avg_sumatera = sub_sum["williamson"].mean()

    fig_sum = go.Figure()
    fig_sum.add_trace(
        go.Bar(
            x=sub_sum_plot["williamson"],
            y=sub_sum_plot["provinsi"],
            orientation="h",
            marker=dict(color=color_map_sum, line=dict(color="rgba(0,0,0,0.1)", width=1)),
            text=[f"{v:.4f}" for v in sub_sum_plot["williamson"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Indeks Williamson: %{x:.4f}<extra></extra>",
        )
    )

    fig_sum.add_vline(
        x=avg_sumatera,
        line=dict(color="#D90429", dash="dash", width=1.8),
        annotation_text=f"Rata-rata Sumatera ({avg_sumatera:.4f})",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#D90429"),
    )

    fig_sum.update_layout(
        xaxis=dict(title="Indeks Williamson (Tahun " + str(tahun) + ")", range=[0, max(sub_sum_plot["williamson"]) * 1.18]),
        yaxis=dict(title=""),
        margin=dict(l=145, r=35, t=25, b=45),
        showlegend=False,
    )

    # Judul kartu dinamis
    decomp_title = f"Dekomposisi Kontribusi Disparitas Wilayah Kepri ({tahun})"
    sumatera_title = f"Perbandingan Ketimpangan Antar-10 Provinsi di Sumatera ({tahun})"

    # Visibility filter mode
    tren_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    decomp_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    sumatera_style = {"flex": "100%", "minWidth": "100%", "marginBottom": "0"}

    if view_mode == "decomp":
        sumatera_style = {"display": "none"}
    elif view_mode == "sumatera":
        tren_style = {"display": "none"}
        decomp_style = {"display": "none"}

    # ── 4. Tabel Ringkasan Komprehensif ────────────────────────────────────
    header_style = {
        "padding": "10px 14px",
        "textAlign": "left",
        "borderBottom": f"2px solid {COLORS['gray_light']}",
        "fontWeight": "600",
        "color": COLORS["primary_dark"],
        "backgroundColor": "#F8FAFC",
    }
    cell_style = {"padding": "9px 14px", "borderBottom": "1px solid #E2E8F0"}

    table_rows = []
    sub_kepri_table = sub_kepri.sort_values("kontribusi_disparitas_pct", ascending=False)
    yn_ref = sub_kepri["yn_provinsi_juta"].iloc[0]

    for _, r in sub_kepri_table.iterrows():
        dev = r["deviasi_persen"]
        dev_color = "#10B981" if dev >= 0 else "#E76F51"
        dev_badge = html.Span(
            f"{'+' if dev >= 0 else ''}{dev:.2f}%",
            style={
                "color": dev_color,
                "fontWeight": "600",
                "backgroundColor": f"{dev_color}18",
                "padding": "3px 8px",
                "borderRadius": "6px",
                "fontSize": "12px",
            },
        )
        table_rows.append(
            html.Tr([
                html.Td(
                    html.Span(
                        r["kab_kota"],
                        style={"fontWeight": "600", "color": KABKOTA_COLORS.get(r["kab_kota"], COLORS["primary_dark"])}
                    ),
                    style=cell_style,
                ),
                html.Td(f"{r['pdrb_perkapita_juta']:.2f} Juta", style=cell_style),
                html.Td(f"{r['jumlah_penduduk']:,}".replace(",", "."), style=cell_style),
                html.Td(f"{r['bobot_penduduk'] * 100:.2f}%", style=cell_style),
                html.Td(dev_badge, style=cell_style),
                html.Td(
                    html.Span(f"{r['kontribusi_disparitas_pct']:.2f}%", style={"fontWeight": "700", "color": COLORS["primary"]}),
                    style=cell_style,
                ),
            ])
        )

    # Baris Referensi Provinsi
    table_rows.append(
        html.Tr([
            html.Td(html.B("Provinsi Kepulauan Riau (Rata-rata Tertimbang)"), style={**cell_style, "backgroundColor": "#F1F5F9"}),
            html.Td(html.B(f"{yn_ref:.2f} Juta"), style={**cell_style, "backgroundColor": "#F1F5F9"}),
            html.Td(html.B(f"{sub_kepri['jumlah_penduduk'].sum():,}".replace(",", ".")), style={**cell_style, "backgroundColor": "#F1F5F9"}),
            html.Td(html.B("100.0%"), style={**cell_style, "backgroundColor": "#F1F5F9"}),
            html.Td(html.B("Acuan (0.0%)"), style={**cell_style, "backgroundColor": "#F1F5F9"}),
            html.Td(html.B("100.0% (Total Disparitas)"), style={**cell_style, "backgroundColor": "#F1F5F9"}),
        ])
    )

    tabel_elegan = html.Div([
        html.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Kabupaten / Kota", style=header_style),
                        html.Th("PDRB Per Kapita", style=header_style),
                        html.Th("Jumlah Penduduk", style=header_style),
                        html.Th("Pangsa Penduduk", style=header_style),
                        html.Th("Deviasi thd Rata-rata", style=header_style),
                        html.Th("Porsi Kontribusi Ketimpangan", style=header_style),
                    ])
                ),
                html.Tbody(table_rows),
            ],
            style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
        ),
        html.Div(
            style={"marginTop": "14px", "padding": "12px 16px", "backgroundColor": "#F8FAFC", "borderRadius": "8px", "fontSize": "12px", "color": COLORS["gray_dark"]},
            children=[
                html.B("Panduan Teori Kriteria Indeks Williamson: "),
                html.Span("• Iw < 0.20: Ketimpangan Rendah  |  • 0.20 ≤ Iw ≤ 0.35: Ketimpangan Sedang  |  • Iw > 0.35: Ketimpangan Tinggi. "),
                html.Span("Formula: Iw = √( Σ (yi - yn)² × (fi / F) ) / yn, dengan yi = PDRB per kapita daerah i, yn = rata-rata tertimbang provinsi, dan fi/F = bobot penduduk.", style={"fontStyle": "italic"}),
            ],
        ),
    ])

    return kpis, fig_tren, fig_decomp, fig_sum, decomp_title, sumatera_title, tren_style, decomp_style, sumatera_style, tabel_elegan
