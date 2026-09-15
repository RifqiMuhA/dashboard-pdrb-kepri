"""
Tab Analisis Shift Share - Kepulauan Riau
Sumber data: data/shift_share_kabupaten_kota_2021_2025.csv & data/shift_share_provinsi_kepri_2021_2025.csv
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.data_loader import DATA
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import COLORS, SEKTOR_COLORS, REFERENCE_LINE_STYLE

# Palet 4 Kuadran Shift Share (Esteban-Marquillas):
_SS_KUADRAN_COLORS = {
    "Kuadran I: Unggulan & Berdaya Saing": "#10B981",       # Hijau Emerald
    "Kuadran II: Tumbuh Cepat, Kalah Saing": "#F2B705",     # Kuning Emas
    "Kuadran III: Tertekan / Tertinggal": "#E76F51",        # Coral / Terracotta
    "Kuadran IV: Spesialisasi Lokal": "#173A66",            # Biru Navy
}


def _get_shiftshare_data():
    df_kk = DATA.get("shift_share_kk", pd.DataFrame())
    df_prov = DATA.get("shift_share_prov", pd.DataFrame())
    return df_kk, df_prov


def layout():
    df_kk, _ = _get_shiftshare_data()
    kk_options = sorted(df_kk["Kabupaten_Kota"].unique().tolist()) if not df_kk.empty else []
    default_kk = "Kota Batam" if "Kota Batam" in kk_options else (kk_options[0] if kk_options else "")

    return html.Div([
        # ── 1. Hero Mascot Insight Card ─────────────────────────────────────
        mascot_insight_bubble(
            title="Analisis Struktur & Daya Saing Ekonomi (Shift Share)",
            content=(
                f"Analisis Shift Share membedah pertumbuhan ekonomi daerah menjadi 3 komponen esensial: "
                f"(1) Efek Pertumbuhan Wilayah Acuan/Provinsi (N), (2) Efek Bauran Industri/Proportional Shift (P), "
                f"dan (3) Efek Keunggulan Kompetitif Lokal/Differential Shift (D). Melalui pemetaan diagram kuadran "
                f"P vs D, pemerintah daerah dapat mengidentifikasi sektor mana yang menjadi lokomotif berdaya saing "
                f"tinggi, sektor yang membutuhkan penguatan efisiensi lokal, dan sektor yang mengalami tekanan struktural."
            ),
            mascot_src="/assets/maskot_1.webp",
            container_id="shiftshare-hero-bubble",
        ),

        # ── 2. KPI Metric Cards ────────────────────────────────────────────
        html.Div(id="ss-kpi-container", style={"marginBottom": "20px"}),

        # ── 3. Filter Controls ─────────────────────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"flex": "1.5", "minWidth": "240px"},
                    children=[
                        html.Label("Wilayah Kabupaten / Kota", className="filter-label"),
                        dcc.Dropdown(
                            id="ss-kk-dropdown",
                            options=[{"label": kk, "value": kk} for kk in kk_options],
                            value=default_kk,
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"flex": "2", "minWidth": "320px"},
                    children=[
                        html.Label("Mode Tampilan Visualisasi", className="filter-label"),
                        dcc.RadioItems(
                            id="ss-view-mode",
                            options=[
                                {"label": " Diagram Kuadran (P vs D)", "value": "quadrant"},
                                {"label": " 3 Komponen (N, P, D)", "value": "components"},
                                {"label": " Tren Tahunan (2021–2025)", "value": "yearly"},
                                {"label": " Tampilkan Semua", "value": "all"},
                            ],
                            value="all",
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

        # ── 4. Visualisasi Grafik dalam Grid Responsif ──────────────────────
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "20px"},
            children=[
                # Chart 1: Diagram Kuadran Shift Share
                html.Div(
                    id="ss-chart-quad-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="ss-quad-title", className="card-title"),
                        dcc.Graph(id="graf-ss-quadrant", style={"height": "460px"}),
                    ],
                ),
                # Chart 2: Bar Chart 3 Komponen
                html.Div(
                    id="ss-chart-comp-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="ss-comp-title", className="card-title"),
                        dcc.Graph(id="graf-ss-components", style={"height": "460px"}),
                    ],
                ),
                # Chart 3: Tren Tahunan
                html.Div(
                    id="ss-chart-year-box",
                    className="card-box",
                    style={"flex": "100%", "minWidth": "100%", "marginBottom": "0"},
                    children=[
                        html.Div(id="ss-year-title", className="card-title"),
                        dcc.Graph(id="graf-ss-yearly", style={"height": "400px"}),
                    ],
                ),
            ],
        ),

        # ── 5. Tabel Klasifikasi Sektoral Lengkap ──────────────────────────
        card("Klasifikasi Kuadran & Dekomposisi 17 Lapangan Usaha", html.Div(id="ss-tabel")),
    ])


@callback(
    Output("ss-kpi-container", "children"),
    Output("graf-ss-quadrant", "figure"),
    Output("graf-ss-components", "figure"),
    Output("graf-ss-yearly", "figure"),
    Output("ss-quad-title", "children"),
    Output("ss-comp-title", "children"),
    Output("ss-year-title", "children"),
    Output("ss-chart-quad-box", "style"),
    Output("ss-chart-comp-box", "style"),
    Output("ss-chart-year-box", "style"),
    Output("ss-tabel", "children"),
    Input("ss-kk-dropdown", "value"),
    Input("ss-view-mode", "value"),
)
def update_shiftshare(kk, view_mode):
    df_kk, df_prov = _get_shiftshare_data()
    if df_kk.empty or not kk:
        empty_fig = go.Figure()
        return html.Div(), empty_fig, empty_fig, empty_fig, "", "", "", {}, {}, {}, html.Div("Data tidak tersedia")

    sub = df_kk[df_kk["Kabupaten_Kota"] == kk].copy()
    if sub.empty:
        empty_fig = go.Figure()
        return html.Div(), empty_fig, empty_fig, empty_fig, "", "", "", {}, {}, {}, html.Div("Data wilayah tidak ditemukan")

    # Klasifikasi Kuadran untuk masing-masing sektor
    def _klasifikasi_ss(r):
        p = r["P_Rerata"]
        d = r["D_Rerata"]
        if p >= 0 and d >= 0:
            return "Kuadran I: Unggulan & Berdaya Saing"
        elif p >= 0 and d < 0:
            return "Kuadran II: Tumbuh Cepat, Kalah Saing"
        elif p < 0 and d < 0:
            return "Kuadran III: Tertekan / Tertinggal"
        else:
            return "Kuadran IV: Spesialisasi Lokal"

    sub["kuadran"] = sub.apply(_klasifikasi_ss, axis=1)

    # Metrik KPI
    n_val = sub["N_Rerata"].iloc[0]
    best_p_row = sub.sort_values("P_Rerata", ascending=False).iloc[0]
    best_d_row = sub.sort_values("D_Rerata", ascending=False).iloc[0]
    total_net_shift = sub["Rerata"].mean()
    n_k1 = len(sub[sub["kuadran"] == "Kuadran I: Unggulan & Berdaya Saing"])

    kpis = html.Div(
        className="kpi-grid",
        children=[
            kpi_card("Efek Acuan Provinsi (N)", f"+{n_val:.2f}%"),
            kpi_card("Bauran Terbaik (P Max)", f"{best_p_row['Kode']} ({best_p_row['P_Rerata']:+.2f}%)"),
            kpi_card("Daya Saing Lokal Terkuat (D Max)", f"{best_d_row['Kode']} ({best_d_row['D_Rerata']:+.2f}%)"),
            kpi_card("Rata-rata Pergeseran Bersih", f"{total_net_shift:+.2f}%"),
            kpi_card("Sektor Kuadran I (Unggulan)", f"{n_k1} dari 17 Sektor"),
        ],
    )

    # ── 1. Figure Diagram Kuadran Shift Share (P vs D) ─────────────────────
    fig_quad = px.scatter(
        sub,
        x="D_Rerata",
        y="P_Rerata",
        color="kuadran",
        text="Kode",
        color_discrete_map=_SS_KUADRAN_COLORS,
        labels={
            "D_Rerata": "Keunggulan Kompetitif Lokal (Differential Shift / D, %)",
            "P_Rerata": "Bauran Industri Provinsi (Proportional Shift / P, %)",
            "kuadran": "Klasifikasi Kuadran",
        },
        hover_data={
            "Lapangan_Usaha": True,
            "Kode": False,
            "P_Rerata": ":+.2f",
            "D_Rerata": ":+.2f",
            "Rerata": ":+.2f",
            "kuadran": True,
        },
    )
    fig_quad.update_traces(
        textposition="top center",
        marker=dict(size=14, line=dict(color="rgba(0,0,0,0.2)", width=1)),
        textfont=dict(size=11, family="Inter, sans-serif", weight="bold"),
    )

    # Garis kuadran D=0 dan P=0
    fig_quad.add_vline(x=0, line=REFERENCE_LINE_STYLE)
    fig_quad.add_hline(y=0, line=REFERENCE_LINE_STYLE)

    # Label kuadran di sudut-sudut diagram
    x_min = min(sub["D_Rerata"].min() * 1.15, -2)
    x_max = max(sub["D_Rerata"].max() * 1.15, 2)
    y_min = min(sub["P_Rerata"].min() * 1.15, -2)
    y_max = max(sub["P_Rerata"].max() * 1.15, 2)

    pad_x = (x_max - x_min) * 0.04
    pad_y = (y_max - y_min) * 0.04
    for xp, yp, xa, ya, lbl in [
        (x_max - pad_x, y_max - pad_y, "right", "top", "I"),
        (x_min + pad_x, y_max - pad_y, "left", "top", "II"),
        (x_min + pad_x, y_min + pad_y, "left", "bottom", "III"),
        (x_max - pad_x, y_min + pad_y, "right", "bottom", "IV"),
    ]:
        fig_quad.add_annotation(
            x=xp, y=yp, text=lbl,
            showarrow=False, xanchor=xa, yanchor=ya,
            font=dict(size=28, color="#CBD5E1", family="Arial Black"),
        )

    fig_quad.update_layout(
        margin=dict(l=60, r=25, t=30, b=100),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=10.5),
        ),
    )

    # ── 2. Figure 3 Komponen Shift Share (Grouped Bar Chart) ───────────────
    sub_sorted_d = sub.sort_values("D_Rerata", ascending=True)
    fig_comp = go.Figure()

    # Differential Shift (D)
    fig_comp.add_trace(
        go.Bar(
            y=[f"{r['Kode']} - {r['Lapangan_Usaha'][:22]}..." if len(r['Lapangan_Usaha']) > 25 else f"{r['Kode']} - {r['Lapangan_Usaha']}" for _, r in sub_sorted_d.iterrows()],
            x=sub_sorted_d["D_Rerata"],
            name="Differential Shift (D)",
            orientation="h",
            marker=dict(color="#10B981"),
            hovertemplate="<b>%{y}</b><br>Diferensial (D): %{x:+.2f}%<extra></extra>",
        )
    )

    # Proportional Shift (P)
    fig_comp.add_trace(
        go.Bar(
            y=[f"{r['Kode']} - {r['Lapangan_Usaha'][:22]}..." if len(r['Lapangan_Usaha']) > 25 else f"{r['Kode']} - {r['Lapangan_Usaha']}" for _, r in sub_sorted_d.iterrows()],
            x=sub_sorted_d["P_Rerata"],
            name="Proportional Shift (P)",
            orientation="h",
            marker=dict(color="#F2B705"),
            hovertemplate="<b>%{y}</b><br>Proporsional (P): %{x:+.2f}%<extra></extra>",
        )
    )

    # National/Provincial Share (N)
    fig_comp.add_trace(
        go.Bar(
            y=[f"{r['Kode']} - {r['Lapangan_Usaha'][:22]}..." if len(r['Lapangan_Usaha']) > 25 else f"{r['Kode']} - {r['Lapangan_Usaha']}" for _, r in sub_sorted_d.iterrows()],
            x=sub_sorted_d["N_Rerata"],
            name="Provincial Share (N)",
            orientation="h",
            marker=dict(color=COLORS["primary"]),
            hovertemplate="<b>%{y}</b><br>Acuan Provinsi (N): %{x:+.2f}%<extra></extra>",
        )
    )

    fig_comp.add_vline(x=0, line=dict(color=COLORS["gray_mid"], width=1))

    fig_comp.update_layout(
        barmode="group",
        xaxis=dict(title="Nilai Komponen Shift Share (%)"),
        yaxis=dict(title=""),
        margin=dict(l=210, r=25, t=30, b=85),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )

    # ── 3. Figure Tren Pertumbuhan Tahunan Sektoral (2021-2025) ────────────
    # Ambil 5 sektor dengan nilai rerata tertinggi untuk grafik garis tren yang bersih
    top_5_sectors = sub.sort_values("Rerata", ascending=False).head(6)
    year_cols = ["2021", "2022", "2023", "2024*", "2025**"]

    fig_yearly = go.Figure()
    for _, r in top_5_sectors.iterrows():
        y_vals = [r[c] for c in year_cols]
        c_code = r["Kode"]
        fig_yearly.add_trace(
            go.Scatter(
                x=[2021, 2022, 2023, 2024, 2025],
                y=y_vals,
                mode="lines+markers",
                name=f"{c_code}. {r['Lapangan_Usaha'][:24]}",
                marker=dict(size=7),
                line=dict(width=2.2),
                hovertemplate="<b>" + r["Lapangan_Usaha"] + "</b><br>Tahun %{x}<br>Pergeseran: %{y:+.2f}%<extra></extra>",
            )
        )

    fig_yearly.add_hline(y=0, line=dict(color=COLORS["gray_mid"], width=1, dash="dot"))

    fig_yearly.update_layout(
        title=dict(text=f"Tren Pertumbuhan Pergeseran Bersih 6 Sektor Tertinggi di {kk} (2021–2025)", font=dict(size=13)),
        xaxis=dict(title="Tahun", tickmode="linear", tick0=2021, dtick=1),
        yaxis=dict(title="Nilai Pergeseran Tahunan (%)"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=10.5),
        ),
        margin=dict(l=55, r=25, t=45, b=90),
    )

    # Judul Kartu
    quad_title = f"Diagram Kuadran Daya Saing P vs D: {kk}"
    comp_title = f"Dekomposisi 3 Komponen Shift Share (N, P, D): {kk}"
    year_title = f"Perkembangan Total Shift Share Tahunan: {kk}"

    # Style filter mode
    quad_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    comp_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    year_style = {"flex": "100%", "minWidth": "100%", "marginBottom": "0"}

    if view_mode == "quadrant":
        comp_style = {"display": "none"}
        year_style = {"display": "none"}
    elif view_mode == "components":
        quad_style = {"display": "none"}
        year_style = {"display": "none"}
    elif view_mode == "yearly":
        quad_style = {"display": "none"}
        comp_style = {"display": "none"}

    # ── 4. Tabel Ringkasan Klasifikasi ────────────────────────────────────
    header_style = {
        "padding": "10px 12px",
        "textAlign": "left",
        "borderBottom": f"2px solid {COLORS['gray_light']}",
        "fontWeight": "600",
        "color": COLORS["primary_dark"],
        "backgroundColor": "#F8FAFC",
    }
    cell_style = {"padding": "8px 12px", "borderBottom": "1px solid #E2E8F0"}

    table_rows = []
    sub_table = sub.sort_values("D_Rerata", ascending=False)

    for _, r in sub_table.iterrows():
        kd = r["kuadran"]
        kd_color = _SS_KUADRAN_COLORS.get(kd, COLORS["primary"])
        badge_kd = html.Span(
            kd.split(":")[0],
            style={
                "color": kd_color,
                "fontWeight": "700",
                "backgroundColor": f"{kd_color}18",
                "padding": "3px 8px",
                "borderRadius": "6px",
                "fontSize": "11.5px",
                "whiteSpace": "nowrap",
            },
        )
        table_rows.append(
            html.Tr([
                html.Td(html.B(r["Kode"], style={"color": COLORS["primary"]}), style=cell_style),
                html.Td(r["Lapangan_Usaha"], style=cell_style),
                html.Td(f"{r['N_Rerata']:+.2f}%", style=cell_style),
                html.Td(
                    html.Span(f"{r['P_Rerata']:+.2f}%", style={"color": "#10B981" if r['P_Rerata'] >= 0 else "#E76F51", "fontWeight": "600"}),
                    style=cell_style,
                ),
                html.Td(
                    html.Span(f"{r['D_Rerata']:+.2f}%", style={"color": "#10B981" if r['D_Rerata'] >= 0 else "#E76F51", "fontWeight": "700"}),
                    style=cell_style,
                ),
                html.Td(html.B(f"{r['Rerata']:+.2f}%"), style=cell_style),
                html.Td(badge_kd, style=cell_style),
            ])
        )

    tabel_elegan = html.Div([
        html.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Kode", style=header_style),
                        html.Th("Lapangan Usaha (Sektor)", style=header_style),
                        html.Th("Provinsi (N)", style=header_style),
                        html.Th("Bauran (P)", style=header_style),
                        html.Th("Diferensial (D)", style=header_style),
                        html.Th("Total Rerata", style=header_style),
                        html.Th("Kuadran Esteban", style=header_style),
                    ])
                ),
                html.Tbody(table_rows),
            ],
            style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
        ),
        html.Div(
            style={"marginTop": "14px", "padding": "12px 16px", "backgroundColor": "#F8FAFC", "borderRadius": "8px", "fontSize": "12px", "color": COLORS["gray_dark"]},
            children=[
                html.B("Interpretasi Kuadran Daya Saing Esteban-Marquillas: "),
                html.Div("• Kuadran I (P > 0, D > 0): Sektor Unggulan & Berdaya Saing Tinggi (Lokomotif pertumbuhan daerah).", style={"marginTop": "4px"}),
                html.Div("• Kuadran II (P > 0, D < 0): Sektor Potensial tapi Kalah Bersaing di Tingkat Lokal (Perlu dorongan efisiensi dan iklim usaha daerah)."),
                html.Div("• Kuadran III (P < 0, D < 0): Sektor Tertekan / Lambat Bertumbuh (Perlu restrukturisasi atau revitalisasi industri)."),
                html.Div("• Kuadran IV (P < 0, D > 0): Sektor Spesialisasi Unggul Daerah (Mampu tumbuh mandiri meskipun tren provinsi melambat)."),
            ],
        ),
    ])

    return kpis, fig_quad, fig_comp, fig_yearly, quad_title, comp_title, year_title, quad_style, comp_style, year_style, tabel_elegan
