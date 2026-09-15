"""
Tab Location Quotient (LQ) - Kepulauan Riau & Profil Provinsi
Sumber data: data/lq_kabupaten_kota_2021_2025.csv & data/lq_provinsi_kepri_2021_2025.csv
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Output, Input

from utils.data_loader import DATA
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import COLORS, REFERENCE_LINE_STYLE

YEAR_OPTIONS = [
    {"label": "2025 (Angka Sangat Sementara)", "value": "2025**"},
    {"label": "2024 (Angka Sementara)", "value": "2024*"},
    {"label": "2023", "value": "2023"},
    {"label": "2022", "value": "2022"},
    {"label": "2021", "value": "2021"},
    {"label": "Rata-rata 5 Tahun (2021–2025)", "value": "Rata_rata"},
]


def _get_lq_data():
    df_kk = DATA.get("lq_kk", pd.DataFrame())
    df_prov = DATA.get("lq_prov", pd.DataFrame())
    return df_kk, df_prov


def layout():
    df_kk, _ = _get_lq_data()
    kk_options = sorted(df_kk["Kabupaten_Kota"].unique().tolist()) if not df_kk.empty else []
    default_kk = "Kota Batam" if "Kota Batam" in kk_options else (kk_options[0] if kk_options else "")

    return html.Div([
        # ── 1. Hero Mascot Insight Card ─────────────────────────────────────
        mascot_insight_bubble(
            title="Analisis Spesialisasi & Sektor Unggulan (Location Quotient)",
            content=(
                "Location Quotient (LQ) mengidentifikasi sektor basis yang menjadi lokomotif ekspor daerah. "
                "Nilai LQ > 1.0 menandakan sektor basis dengan konsentrasi produksi melebihi kebutuhan lokal sehingga "
                "berpotensi memasok pasar luar daerah. Nilai LQ < 1.0 menunjukkan sektor non-basis yang belum mencukupi "
                "kebutuhan internal (bergantung pada pasokan luar). Skala warna divergen berpusat di LQ = 1.0 "
                "memudahkan pemangku kebijakan membedakan sektor unggulan daerah dalam sekali pandang."
            ),
            mascot_src="/assets/maskot_1.webp",
            container_id="lq-hero-bubble",
        ),

        # ── 2. KPI Metric Cards ────────────────────────────────────────────
        html.Div(id="lq-kpi-container", style={"marginBottom": "20px"}),

        # ── 3. Filter Controls ─────────────────────────────────────────────
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    style={"flex": "1.2", "minWidth": "220px"},
                    children=[
                        html.Label("Tahun Analisis", className="filter-label"),
                        dcc.Dropdown(
                            id="lq-tahun-dropdown",
                            options=YEAR_OPTIONS,
                            value="2025**",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    style={"flex": "1.5", "minWidth": "240px"},
                    children=[
                        html.Label("Wilayah Profil (Kab/Kota)", className="filter-label"),
                        dcc.Dropdown(
                            id="lq-kk-dropdown",
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
                            id="lq-view-mode",
                            options=[
                                {"label": " Matriks Heatmap Se-Kepri", "value": "heatmap"},
                                {"label": " Profil Wilayah Terpilih", "value": "profile"},
                                {"label": " Profil Provinsi vs Nasional", "value": "provinsi"},
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

        # ── 4. Visualisasi Grafik dalam Flexbox Responsif ──────────────────
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "20px"},
            children=[
                # Chart 1: Heatmap Matriks LQ Se-Kepri
                html.Div(
                    id="lq-chart-heatmap-box",
                    className="card-box",
                    style={"flex": "100%", "minWidth": "100%", "marginBottom": "0"},
                    children=[
                        html.Div(id="lq-heatmap-title", className="card-title"),
                        dcc.Graph(id="graf-lq-heatmap", style={"height": "520px"}),
                    ],
                ),
                # Chart 2: Bar Chart Profil Wilayah Terpilih
                html.Div(
                    id="lq-chart-profile-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="lq-profile-title", className="card-title"),
                        dcc.Graph(id="graf-lq-profile", style={"height": "460px"}),
                    ],
                ),
                # Chart 3: Bar Chart Profil Provinsi Kepri vs Nasional
                html.Div(
                    id="lq-chart-prov-box",
                    className="card-box",
                    style={"flex": "1", "minWidth": "460px", "marginBottom": "0"},
                    children=[
                        html.Div(id="lq-prov-title", className="card-title"),
                        dcc.Graph(id="graf-lq-prov", style={"height": "460px"}),
                    ],
                ),
            ],
        ),

        # ── 5. Tabel Ringkasan Sektor Basis vs Non-Basis ───────────────────
        card("Identifikasi Komprehensif Sektor Basis & Non-Basis", html.Div(id="lq-tabel")),
    ])


@callback(
    Output("lq-kpi-container", "children"),
    Output("graf-lq-heatmap", "figure"),
    Output("graf-lq-profile", "figure"),
    Output("graf-lq-prov", "figure"),
    Output("lq-heatmap-title", "children"),
    Output("lq-profile-title", "children"),
    Output("lq-prov-title", "children"),
    Output("lq-chart-heatmap-box", "style"),
    Output("lq-chart-profile-box", "style"),
    Output("lq-chart-prov-box", "style"),
    Output("lq-tabel", "children"),
    Input("lq-tahun-dropdown", "value"),
    Input("lq-kk-dropdown", "value"),
    Input("lq-view-mode", "value"),
)
def update_lq(tahun_col, kk, view_mode):
    df_kk, df_prov = _get_lq_data()
    if df_kk.empty or not kk or tahun_col not in df_kk.columns:
        empty_fig = go.Figure()
        return html.Div(), empty_fig, empty_fig, empty_fig, "", "", "", {}, {}, {}, html.Div("Data tidak tersedia")

    sub_kk = df_kk[df_kk["Kabupaten_Kota"] == kk].copy()
    sub_kk["lq_val"] = sub_kk[tahun_col].astype(float)
    sub_kk["status"] = sub_kk["lq_val"].apply(lambda x: "Basis" if x >= 1.0 else "Non Basis")

    # Metrik KPI untuk wilayah terpilih
    basis_rows = sub_kk[sub_kk["lq_val"] >= 1.0]
    n_basis = len(basis_rows)
    top_basis = sub_kk.sort_values("lq_val", ascending=False).iloc[0]
    lowest_lq = sub_kk.sort_values("lq_val", ascending=True).iloc[0]
    avg_lq_basis = basis_rows["lq_val"].mean() if not basis_rows.empty else 0.0

    kpis = html.Div(
        className="kpi-grid",
        children=[
            kpi_card(f"Jumlah Sektor Basis ({kk})", f"{n_basis} dari 17 Sektor"),
            kpi_card("Sektor Paling Spesialis (LQ Max)", f"{top_basis['Kode']} (LQ {top_basis['lq_val']:.2f})"),
            kpi_card("Rata-rata LQ Sektor Unggulan", f"{avg_lq_basis:.2f}"),
            kpi_card("Sektor Paling Bergantung Impor", f"{lowest_lq['Kode']} (LQ {lowest_lq['lq_val']:.2f})"),
            kpi_card("Tingkat Diversifikasi Ekonomi", "Tinggi" if n_basis >= 8 else ("Moderat" if n_basis >= 5 else "Terkonsentrasi")),
        ],
    )

    # ── 1. Figure Heatmap Matriks Se-Kepri ─────────────────────────────────
    # Susun matriks: baris = Lapangan Usaha, kolom = Kabupaten/Kota
    df_kk_pivot = df_kk.copy()
    def _format_sector_label(row):
        nama = str(row["Lapangan_Usaha"])
        if len(nama) > 36:
            nama = nama[:34] + "..."
        return f"{row['Kode']}. {nama}"

    df_kk_pivot["sektor_label"] = df_kk_pivot.apply(_format_sector_label, axis=1)
    pivot = df_kk_pivot.pivot(index="sektor_label", columns="Kabupaten_Kota", values=tahun_col)

    # Singkatkan nama kabupaten/kota untuk header kolom heatmap yang proporsional
    pivot.columns = [c.replace("Kabupaten ", "Kab. ").replace("Kota ", "Kota ") for c in pivot.columns]

    # Skala Warna Divergen Berpusat di LQ = 1.0:
    # 0.0 s.d 1.0 : Skala coral merah lembut (Non-Basis)
    # 1.0         : Putih netral (Ambang Batas)
    # 1.0 s.d Max : Biru muda ke Navy gelap pekat (Basis Unggulan)
    max_lq = float(pivot.values.max())
    midpoint_ratio = 1.0 / max_lq if max_lq > 1.0 else 0.5

    fig_heatmap = px.imshow(
        pivot,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#FCA5A5"],              # Coral muda (LQ = 0)
            [midpoint_ratio * 0.9, "#FEE2E2"], # Coral sangat pucat mendekati 1
            [midpoint_ratio, "#FFFFFF"],   # Putih netral di ambang batas 1.0
            [midpoint_ratio + (1 - midpoint_ratio) * 0.15, "#38BDF8"], # Biru cerah (LQ ~ 1.5 - 2)
            [midpoint_ratio + (1 - midpoint_ratio) * 0.4, "#1D4ED8"],  # Biru royal (LQ ~ 3 - 5)
            [1.0, "#0C203A"],              # Navy sangat gelap (LQ ekstrem > 7)
        ],
        labels=dict(color="Indeks LQ"),
    )

    fig_heatmap.update_traces(
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate="<b>%{y}</b><br>Wilayah: %{x}<br>Nilai LQ: %{z:.2f}<extra></extra>",
    )

    fig_heatmap.update_layout(
        xaxis=dict(title="", tickangle=-20, tickfont=dict(size=11, weight="bold", color=COLORS["primary_dark"])),
        yaxis=dict(title="", tickfont=dict(size=11, color=COLORS["gray_dark"])),
        margin=dict(l=280, r=25, t=25, b=60),
        coloraxis_colorbar=dict(
            title="Indeks LQ",
            tickvals=[0, 1.0, 2.0, 4.0, round(max_lq, 1)],
            ticktext=["0 (Kecil)", "1.0 (Ambang Basis)", "2.0 (Spesialis)", "4.0+", f"{max_lq:.1f} (Maks)"],
            lenmode="fraction",
            len=0.88,
        ),
    )

    # ── 2. Figure Bar Chart Profil Wilayah Terpilih ────────────────────────
    sub_kk_sorted = sub_kk.sort_values("lq_val", ascending=True)
    bar_colors = [
        "#10B981" if v >= 1.0 else "#94A3B8" for v in sub_kk_sorted["lq_val"]
    ]

    fig_profile = go.Figure()
    fig_profile.add_trace(
        go.Bar(
            y=[f"{r['Kode']}. {r['Lapangan_Usaha'][:22]}..." if len(r['Lapangan_Usaha']) > 24 else f"{r['Kode']}. {r['Lapangan_Usaha']}" for _, r in sub_kk_sorted.iterrows()],
            x=sub_kk_sorted["lq_val"],
            orientation="h",
            marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0.12)", width=1)),
            text=[f"{v:.2f}" for v in sub_kk_sorted["lq_val"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Nilai LQ: %{x:.2f}<br>Status: %{text}<extra></extra>",
        )
    )

    # Garis vertikal referensi LQ = 1.0
    fig_profile.add_vline(
        x=1.0,
        line=dict(color="#D90429", dash="dash", width=2),
        annotation_text="Ambang Batas Sektor Basis (LQ = 1.0)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#D90429"),
    )

    fig_profile.update_layout(
        xaxis=dict(title=f"Nilai Location Quotient ({tahun_col})", range=[0, max(sub_kk_sorted["lq_val"]) * 1.18]),
        yaxis=dict(title=""),
        margin=dict(l=175, r=35, t=25, b=45),
        showlegend=False,
    )

    # ── 3. Figure Bar Chart Profil Provinsi Kepri vs Nasional ─────────────
    # Ambil kolom yang cocok di df_prov
    prov_col = "2025**" if "2025**" in df_prov.columns else ("Rata-rata" if "Rata-rata" in df_prov.columns else df_prov.columns[1])
    if tahun_col in df_prov.columns:
        prov_col = tahun_col
    elif tahun_col == "Rata_rata" and "Rata-rata" in df_prov.columns:
        prov_col = "Rata-rata"

    df_prov_sorted = df_prov.copy()
    df_prov_sorted["lq_val"] = df_prov_sorted[prov_col].astype(float)
    df_prov_sorted = df_prov_sorted.sort_values("lq_val", ascending=True)

    prov_bar_colors = [
        COLORS["primary"] if v >= 1.0 else "#CBD5E1" for v in df_prov_sorted["lq_val"]
    ]

    fig_prov = go.Figure()
    fig_prov.add_trace(
        go.Bar(
            y=[f"{r['Lapangan Usaha'][:24]}..." if len(r['Lapangan Usaha']) > 26 else r['Lapangan Usaha'] for _, r in df_prov_sorted.iterrows()],
            x=df_prov_sorted["lq_val"],
            orientation="h",
            marker=dict(color=prov_bar_colors, line=dict(color="rgba(0,0,0,0.12)", width=1)),
            text=[f"{v:.2f}" for v in df_prov_sorted["lq_val"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>LQ Provinsi thd Nasional: %{x:.2f}<extra></extra>",
        )
    )

    fig_prov.add_vline(
        x=1.0,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=2),
        annotation_text="Batas Basis Nasional (LQ = 1.0)",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color=COLORS["accent_dark"]),
    )

    fig_prov.update_layout(
        xaxis=dict(title=f"Location Quotient Kepri thd Nasional ({prov_col})", range=[0, max(df_prov_sorted["lq_val"]) * 1.18]),
        yaxis=dict(title=""),
        margin=dict(l=175, r=35, t=25, b=45),
        showlegend=False,
    )

    # Judul Kartu
    tahun_label = dict(YEAR_OPTIONS).get(tahun_col, tahun_col)
    heatmap_title = f"Matriks Location Quotient 17 Lapangan Usaha Se-Kepulauan Riau ({tahun_label})"
    profile_title = f"Profil Spesialisasi Sektor Basis di {kk} ({tahun_label})"
    prov_title = f"Spesialisasi Sektor Basis Provinsi Kepulauan Riau terhadap Nasional"

    # Style filter mode
    heatmap_style = {"flex": "100%", "minWidth": "100%", "marginBottom": "0"}
    profile_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}
    prov_style = {"flex": "1", "minWidth": "460px", "marginBottom": "0"}

    if view_mode == "heatmap":
        profile_style = {"display": "none"}
        prov_style = {"display": "none"}
    elif view_mode == "profile":
        heatmap_style = {"display": "none"}
        prov_style = {"display": "none"}
    elif view_mode == "provinsi":
        heatmap_style = {"display": "none"}
        profile_style = {"display": "none"}

    # ── 4. Tabel Ringkasan Sektor Basis vs Non-Basis ───────────────────────
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
    sub_table = sub_kk.sort_values("lq_val", ascending=False)

    for _, r in sub_table.iterrows():
        is_basis = r["lq_val"] >= 1.0
        status_color = "#10B981" if is_basis else "#64748B"
        badge_status = html.Span(
            "Basis (Ekspor)" if is_basis else "Non Basis (Lokal/Impor)",
            style={
                "color": status_color,
                "fontWeight": "700",
                "backgroundColor": f"{status_color}18",
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
                html.Td(
                    html.Span(f"{r['lq_val']:.2f}", style={"fontWeight": "700", "color": COLORS["primary_dark"] if is_basis else COLORS["gray_mid"]}),
                    style=cell_style,
                ),
                html.Td(badge_status, style=cell_style),
                html.Td(
                    "Memiliki surplus produksi untuk memasok wilayah lain" if is_basis else "Memerlukan pasokan dari luar wilayah untuk mencukupi konsumsi",
                    style={**cell_style, "color": COLORS["gray_dark"], "fontSize": "12px"},
                ),
            ])
        )

    tabel_elegan = html.Div([
        html.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Kode", style=header_style),
                        html.Th("Lapangan Usaha", style=header_style),
                        html.Th("Nilai LQ", style=header_style),
                        html.Th("Status Klasifikasi", style=header_style),
                        html.Th("Implikasi Perekonomian Regional", style=header_style),
                    ])
                ),
                html.Tbody(table_rows),
            ],
            style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
        ),
        html.Div(
            style={"marginTop": "14px", "padding": "12px 16px", "backgroundColor": "#F8FAFC", "borderRadius": "8px", "fontSize": "12px", "color": COLORS["gray_dark"]},
            children=[
                html.B("Panduan Teori Location Quotient (LQ): "),
                html.Span("• LQ > 1.0 (Sektor Basis): Konsentrasi ekonomi daerah lebih tinggi daripada acuan provinsi/nasional. Menghasilkan surplus ekspor dan menarik arus modal masuk. "),
                html.Span("• LQ < 1.0 (Sektor Non-Basis): Menunjukkan ketergantungan pasokan impor dari luar wilayah untuk konsumsi lokal."),
            ],
        ),
    ])

    return kpis, fig_heatmap, fig_profile, fig_prov, heatmap_title, profile_title, prov_title, heatmap_style, profile_style, prov_style, tabel_elegan
