"""
Tab Indeks Bonet - Kepulauan Riau & Komparasi Regional
Sumber data: data/williamson_bonet_kepri.csv & data/williamson_bonet_sumatera.csv
(diekstrak dari data/data mentah pdrb adhk untuk williamson bonnet.xlsx)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.data_loader import DATA
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import COLORS, KABKOTA_COLORS


def _get_bonet_data():
    df_kepri = DATA.get("williamson_bonet_kepri", pd.DataFrame())
    df_sumatera = DATA.get("williamson_bonet_sumatera", pd.DataFrame())
    return df_kepri, df_sumatera


def layout():
    df_kepri, _ = _get_bonet_data()
    years = sorted(df_kepri["tahun"].unique().tolist()) if not df_kepri.empty else [2021, 2022, 2023, 2024, 2025]
    latest_year = max(years)

    return html.Div([
        # ── 1. Hero Mascot Insight Card ─────────────────────────────────────
        mascot_insight_bubble(
            title="Analisis Deviasi & Disparitas Relatif (Indeks Bonet)",
            content=(
                f"Indeks Bonet mengukur deviasi proporsional PDRB per kapita masing-masing kabupaten/kota "
                f"terhadap rata-rata provinsi. Di Kepulauan Riau pada tahun {latest_year}, disparitas sangat mencolok: "
                f"Kepulauan Anambas (+140.4%) dan Natuna (+80.3%) berada jauh di atas rata-rata provinsi berkat PDRB migas "
                f"dan populasi kecil. Sebaliknya, Kabupaten Lingga (-66.5%) dan Karimun (-56.9%) mengalami kesenjangan negatif "
                f"terbesar, dengan rasio per kapita antara daerah tertinggi dan terendah mencapai lebih dari 7 kali lipat."
            ),
            mascot_src="/assets/maskot_1.webp",
            container_id="bonet-hero-bubble",
        ),

        # ── 2. KPI Metric Cards ────────────────────────────────────────────
        html.Div(id="bonet-kpi-container", style={"marginBottom": "20px"}),

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
                            id="bonet-tahun",
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
                            id="bonet-view-mode",
                            options=[
                                {"label": " Deviasi Wilayah & Tren", "value": "dev_trend"},
                                {"label": " Komparasi Bonet Sumatera", "value": "sumatera"},
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

        # ── 4. Visualisasi Grafik dalam Flexbox Responsif ──────────────────
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "20px"},
            children=[
                # Chart 1: Diverging Bar Chart Deviasi Relatif
                html.Div(
                    id="bonet-chart-diverge-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="bonet-diverge-title", className="card-title"),
                        dcc.Graph(id="graf-bonet-diverge", style={"height": "430px"}),
                    ],
                ),
                # Chart 2: Multi-Line Chart Tren Bonet Multi-Tahun
                html.Div(
                    id="bonet-chart-trend-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div("Tren Indeks Bonet per Kab/Kota (2021–2025)", className="card-title"),
                        dcc.Graph(id="graf-bonet-trend", style={"height": "430px"}),
                    ],
                ),
                # Chart 3: Komparasi Rata-rata Bonet 10 Provinsi Sumatera
                html.Div(
                    id="bonet-chart-sumatera-box",
                    className="card-box",
                    style={"flex": "100%", "minWidth": "100%", "marginBottom": "0"},
                    children=[
                        html.Div(id="bonet-sumatera-title", className="card-title"),
                        dcc.Graph(id="graf-bonet-sumatera", style={"height": "380px"}),
                    ],
                ),
            ],
        ),

        # ── 5. Tabel Ringkasan Komprehensif ────────────────────────────────
        card("Daftar Klasifikasi Deviasi PDRB Per Kapita & Indeks Bonet Regional", html.Div(id="bonet-tabel")),
    ])


@callback(
    Output("bonet-kpi-container", "children"),
    Output("graf-bonet-diverge", "figure"),
    Output("graf-bonet-trend", "figure"),
    Output("graf-bonet-sumatera", "figure"),
    Output("bonet-diverge-title", "children"),
    Output("bonet-sumatera-title", "children"),
    Output("bonet-chart-diverge-box", "style"),
    Output("bonet-chart-trend-box", "style"),
    Output("bonet-chart-sumatera-box", "style"),
    Output("bonet-tabel", "children"),
    Input("bonet-tahun", "value"),
    Input("bonet-view-mode", "value"),
)
def update_bonet(tahun, view_mode):
    df_kepri, df_sum = _get_bonet_data()
    if df_kepri.empty or df_sum.empty:
        empty_fig = go.Figure()
        return html.Div(), empty_fig, empty_fig, empty_fig, "", "", {}, {}, {}, html.Div("Data tidak tersedia")

    sub_kepri = df_kepri[df_kepri["tahun"] == tahun].copy()
    sub_sum = df_sum[df_sum["tahun"] == tahun].copy()

    # Metrik KPI
    mean_bonet = sub_kepri["indeks_bonet"].mean()
    top_surplus = sub_kepri.sort_values("deviasi_persen", ascending=False).iloc[0]
    top_deficit = sub_kepri.sort_values("deviasi_persen", ascending=True).iloc[0]
    ratio_rich_poor = top_surplus["pdrb_perkapita_juta"] / top_deficit["pdrb_perkapita_juta"]
    yn_ref = sub_kepri["yn_provinsi_juta"].iloc[0]

    kpis = html.Div(
        className="kpi-grid",
        children=[
            kpi_card(f"Rata-rata Indeks Bonet ({tahun})", f"{mean_bonet:.4f}"),
            kpi_card("Surplus Deviasi Tertinggi", f"{top_surplus['kab_kota'].replace('Kabupaten ', '').replace('Kota ', '')} (+{top_surplus['deviasi_persen']:.1f}%)"),
            kpi_card("Defisit Deviasi Terbesar", f"{top_deficit['kab_kota'].replace('Kabupaten ', '').replace('Kota ', '')} ({top_deficit['deviasi_persen']:.1f}%)"),
            kpi_card("Rasio Terkaya vs Terendah", f"{ratio_rich_poor:.2f}x Lipat"),
            kpi_card(f"PDRB Per Kapita Acuan ({tahun})", f"{yn_ref:.2f} Juta Rp"),
        ],
    )

    # ── 1. Figure Diverging Bar Chart Deviasi Relatif (%) ──────────────────
    sub_sorted = sub_kepri.sort_values("deviasi_persen", ascending=True)
    diverge_colors = [
        "#10B981" if v >= 0 else "#E76F51" for v in sub_sorted["deviasi_persen"]
    ]

    fig_diverge = go.Figure()
    fig_diverge.add_trace(
        go.Bar(
            x=sub_sorted["deviasi_persen"],
            y=[k.replace("Kabupaten ", "Kab. ").replace("Kota ", "Kota ") for k in sub_sorted["kab_kota"]],
            orientation="h",
            marker=dict(color=diverge_colors, line=dict(color="rgba(0,0,0,0.12)", width=1)),
            text=[f"{'+' if v >= 0 else ''}{v:.1f}%" for v in sub_sorted["deviasi_persen"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Deviasi: %{x:.2f}%<br>"
                "<extra></extra>"
            ),
        )
    )

    # Garis tengah 0% (Patokan Rata-rata Provinsi)
    fig_diverge.add_vline(
        x=0, line=dict(color=COLORS["primary_dark"], width=2)
    )

    min_dev = sub_sorted["deviasi_persen"].min()
    max_dev = sub_sorted["deviasi_persen"].max()
    fig_diverge.update_layout(
        xaxis=dict(
            title="Persentase Deviasi PDRB Per Kapita terhadap Rata-rata Provinsi (%)",
            range=[min_dev * 1.38 if min_dev < 0 else -20, max_dev * 1.25],
            zeroline=True,
            zerolinecolor=COLORS["primary_dark"],
            zerolinewidth=2,
        ),
        yaxis=dict(title=""),
        margin=dict(l=165, r=40, t=25, b=45),
        showlegend=False,
    )

    # ── 2. Figure Multi-Line Chart Tren Indeks Bonet ───────────────────────
    fig_trend = go.Figure()
    for kk in sorted(df_kepri["kab_kota"].unique()):
        kk_sub = df_kepri[df_kepri["kab_kota"] == kk].sort_values("tahun")
        c_color = KABKOTA_COLORS.get(kk, COLORS["primary"])
        is_highlight = kk in ["Kabupaten Kepulauan Anambas", "Kabupaten Lingga", "Kota Batam"]
        fig_trend.add_trace(
            go.Scatter(
                x=kk_sub["tahun"],
                y=kk_sub["indeks_bonet"],
                mode="lines+markers",
                name=kk.replace("Kabupaten ", "Kab. ").replace("Kota ", "Kota "),
                line=dict(color=c_color, width=3 if is_highlight else 1.8),
                marker=dict(size=7 if is_highlight else 5),
                hovertemplate="<b>" + kk + "</b><br>Tahun %{x}<br>Indeks Bonet: %{y:.4f}<extra></extra>",
            )
        )

    fig_trend.update_layout(
        xaxis=dict(tickmode="linear", tick0=2021, dtick=1, title="Tahun"),
        yaxis=dict(title="Indeks Bonet |(Yi / Yn) - 1|"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        margin=dict(l=55, r=25, t=25, b=80),
    )

    # ── 3. Figure Komparasi Rata-rata Bonet Sumatera ────────────────────────
    sub_sum_plot = sub_sum.sort_values("bonet_mean", ascending=True)
    color_map_sum = [
        COLORS["accent"] if p == "Kepulauan Riau" else COLORS["primary_light"]
        for p in sub_sum_plot["provinsi"]
    ]
    avg_bonet_sum = sub_sum["bonet_mean"].mean()

    fig_sum = go.Figure()
    fig_sum.add_trace(
        go.Bar(
            x=sub_sum_plot["bonet_mean"],
            y=sub_sum_plot["provinsi"],
            orientation="h",
            marker=dict(color=color_map_sum, line=dict(color="rgba(0,0,0,0.1)", width=1)),
            text=[f"{v:.4f}" for v in sub_sum_plot["bonet_mean"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Rata-rata Indeks Bonet: %{x:.4f}<extra></extra>",
        )
    )

    fig_sum.add_vline(
        x=avg_bonet_sum,
        line=dict(color="#D90429", dash="dash", width=1.8),
        annotation_text=f"Rata-rata Sumatera ({avg_bonet_sum:.4f})",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color="#D90429"),
    )

    fig_sum.update_layout(
        xaxis=dict(title="Rata-rata Indeks Bonet Kabupaten/Kota (Tahun " + str(tahun) + ")", range=[0, max(sub_sum_plot["bonet_mean"]) * 1.2]),
        yaxis=dict(title=""),
        margin=dict(l=145, r=35, t=25, b=45),
        showlegend=False,
    )

    diverge_title = f"Deviasi PDRB Per Kapita terhadap Rata-rata Provinsi Kepri ({tahun})"
    sumatera_title = f"Perbandingan Rata-rata Indeks Bonet Antar-10 Provinsi di Sumatera ({tahun})"

    # Filter mode styles
    diverge_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    trend_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    sumatera_style = {"flex": "100%", "minWidth": "100%", "marginBottom": "0"}

    if view_mode == "dev_trend":
        sumatera_style = {"display": "none"}
    elif view_mode == "sumatera":
        diverge_style = {"display": "none"}
        trend_style = {"display": "none"}

    # ── 4. Tabel Ringkasan Bonet ───────────────────────────────────────────
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
    sub_kepri_table = sub_kepri.sort_values("pdrb_perkapita_juta", ascending=False)

    for _, r in sub_kepri_table.iterrows():
        dev = r["deviasi_persen"]
        dev_color = "#10B981" if dev >= 0 else "#E76F51"
        status_dev = "Di Atas Rata-rata Provinsi" if dev >= 0 else "Di Bawah Rata-rata Provinsi"
        rasio_thd_prov = r["pdrb_perkapita_juta"] / yn_ref

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
                html.Td(f"{rasio_thd_prov:.2f}x", style=cell_style),
                html.Td(
                    html.Span(f"{r['indeks_bonet']:.4f}", style={"fontWeight": "700", "color": COLORS["primary"]}),
                    style=cell_style,
                ),
                html.Td(
                    html.Span(
                        f"{'+' if dev >= 0 else ''}{dev:.2f}%",
                        style={
                            "color": dev_color,
                            "fontWeight": "600",
                            "backgroundColor": f"{dev_color}18",
                            "padding": "3px 8px",
                            "borderRadius": "6px",
                            "fontSize": "12px",
                        },
                    ),
                    style=cell_style,
                ),
                html.Td(
                    html.Span(
                        status_dev,
                        style={"color": dev_color, "fontWeight": "500", "fontSize": "12px"}
                    ),
                    style=cell_style,
                ),
            ])
        )

    tabel_elegan = html.Div([
        html.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Kabupaten / Kota", style=header_style),
                        html.Th("PDRB Per Kapita", style=header_style),
                        html.Th("Rasio thd Provinsi", style=header_style),
                        html.Th("Indeks Bonet (IB)", style=header_style),
                        html.Th("Persentase Deviasi", style=header_style),
                        html.Th("Status Kesenjangan", style=header_style),
                    ])
                ),
                html.Tbody(table_rows),
            ],
            style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
        ),
        html.Div(
            style={"marginTop": "14px", "padding": "12px 16px", "backgroundColor": "#F8FAFC", "borderRadius": "8px", "fontSize": "12px", "color": COLORS["gray_dark"]},
            children=[
                html.B("Panduan Teori Indeks Bonet: "),
                html.Span("Indeks Bonet (IBi) dihitung dengan formula | (yi / yn) - 1 |, mengukur besarnya jarak penyimpangan ekonomi suatu wilayah dari rata-rata acuan tanpa pembobotan penduduk. "),
                html.Span("Semakin mendekati nol, perekonomian wilayah tersebut semakin serupa dengan rata-rata provinsi. Nilai yang besar menunjukkan deviasi tajam (baik surplus maupun defisit).", style={"fontStyle": "italic"}),
            ],
        ),
    ])

    return kpis, fig_diverge, fig_trend, fig_sum, diverge_title, sumatera_title, diverge_style, trend_style, sumatera_style, tabel_elegan
