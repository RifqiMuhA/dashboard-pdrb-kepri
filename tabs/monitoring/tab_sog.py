from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, get_years_list
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import get_sektor_color_by_name, COLORS

years = get_years_list()


def layout():
    return html.Div(
        [
            html.Div(id="sog-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        style={"minWidth": "240px"},
                        children=[
                            html.Label("Dimensi Analisis", className="filter-label"),
                            dcc.Dropdown(
                                id="sog-kategori",
                                options=[
                                    {"label": "17 Lapangan Usaha", "value": "lapangan_usaha"},
                                    {"label": "Komponen Pengeluaran", "value": "pengeluaran"},
                                ],
                                value="lapangan_usaha",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Basis Laju", className="filter-label"),
                            dcc.Dropdown(
                                id="sog-metrik",
                                options=[
                                    {"label": "Year-on-Year (y-on-y)", "value": "sog_y_on_y"},
                                    {"label": "Quarter-to-Quarter (q-to-q)", "value": "sog_q_to_q"},
                                ],
                                value="sog_y_on_y",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun", className="filter-label"),
                            dcc.Dropdown(
                                id="sog-tahun",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=max(years) if years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="sog-kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1.3fr 1.3fr", "gap": "20px"},
                children=[
                    card(
                        "Dekomposisi Sektor Pendorong vs Penahan Pertumbuhan (Tahun Terpilih)",
                        dcc.Graph(id="graf-sog-diverging"),
                    ),
                    card(
                        "Dinamika Sumber Pertumbuhan dari Tahun ke Tahun (2021–2025)",
                        dcc.Graph(id="graf-sog-stacked"),
                    ),
                ],
            ),
        ]
    )


@callback(
    Output("sog-insight-container", "children"),
    Output("sog-kpi-container", "children"),
    Output("graf-sog-diverging", "figure"),
    Output("graf-sog-stacked", "figure"),
    Input("sog-kategori", "value"),
    Input("sog-metrik", "value"),
    Input("sog-tahun", "value"),
)
def update_sog(kategori, metrik_col, tahun):
    df_sog = DATA.get("sumber_pertumbuhan", None)
    if df_sog is None or df_sog.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    sub_kat = df_sog[df_sog["kategori"] == kategori].copy()
    
    # Ambil baris Total PDRB
    row_pdrb = sub_kat[(sub_kat["kode"] == "PDRB") & (sub_kat["tahun"] == tahun)]
    pertumbuhan_total = row_pdrb[metrik_col].iloc[0] if not row_pdrb.empty else 0.0

    # Ambil rincian sektor/komponen (tanpa baris PDRB total)
    sub_sectors = sub_kat[sub_kat["kode"] != "PDRB"].copy()
    sub_tahun = sub_sectors[sub_sectors["tahun"] == tahun].sort_values(metrik_col, ascending=True)

    # Identifikasi kontributor terbesar dan terkecil
    best_row = sub_tahun.iloc[-1] if not sub_tahun.empty else None
    worst_row = sub_tahun.iloc[0] if not sub_tahun.empty else None

    metrik_label = "y-on-y" if "y_on_y" in metrik_col else "q-to-q"

    best_title = f"{best_row['uraian']} ({best_row['kode']})" if best_row is not None else "-"
    worst_title = f"{worst_row['uraian']} ({worst_row['kode']})" if worst_row is not None else "-"

    insight_content = [
        f"Pada tahun {tahun}, laju pertumbuhan ekonomi Kepri secara agregat tercatat ",
        html.Strong(f"{pertumbuhan_total:+.2f}% ({metrik_label})", className="chat-bubble-highlight"),
        f". Hasil dekomposisi sumber pertumbuhan ({'17 Lapangan Usaha' if kategori == 'lapangan_usaha' else 'Komponen Pengeluaran'}) menunjukkan bahwa motor pendorong utama adalah ",
        html.Strong(f"{best_title}", className="chat-bubble-highlight"),
        f" dengan kontribusi impresif sebesar ",
        html.Strong(f"{best_row[metrik_col]:+.2f}% poin", className="chat-bubble-highlight") if best_row is not None else "",
        f". Di sisi lain, faktor yang menahan laju ekonomi terbesar adalah ",
        html.Strong(f"{worst_title}", className="chat-bubble-highlight"),
        f" dengan kontribusi ",
        html.Strong(f"{worst_row[metrik_col]:+.2f}% poin", className="chat-bubble-highlight") if worst_row is not None else "",
        ". Hal ini menegaskan pentingnya menjaga stabilitas sektor pendorong sebagai jangkar ekonomi regional.",
    ]

    insight = mascot_insight_bubble(
        title=f"Insight Sumber Pertumbuhan Ekonomi (SOG) Kepri ({tahun})",
        content=insight_content,
        mascot_src="/assets/maskot_1.webp",
    )

    kpis = [
        kpi_card(
            f"Pertumbuhan PDRB Kepri ({metrik_label}, {tahun})",
            f"{pertumbuhan_total:+.2f}%",
        ),
        kpi_card(
            f"Pendorong Utama ({tahun})",
            f"{best_row['kode']} ({best_row[metrik_col]:+.2f}%)" if best_row is not None else "-",
        ),
        kpi_card(
            f"Faktor Penahan ({tahun})",
            f"{worst_row['kode']} ({worst_row[metrik_col]:+.2f}%)" if worst_row is not None else "-",
        ),
    ]

    # 1. Figure Diverging Bar Chart
    # Warna hijau/navy untuk positif, merah/coral untuk negatif
    bar_colors = [
        "#2A9D8F" if val >= 0 else "#E76F51"
        for val in sub_tahun[metrik_col]
    ]
    labels_clean = [
        u[:30] + "..." if len(u) > 30 else u
        for u in sub_tahun["uraian"]
    ]

    fig_diverging = go.Figure(
        go.Bar(
            y=labels_clean,
            x=sub_tahun[metrik_col],
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{v:+.2f}%" for v in sub_tahun[metrik_col]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>SOG: %{x:+.2f}% poin persentase<extra></extra>",
        )
    )
    fig_diverging.update_layout(
        xaxis_title="Sumber Pertumbuhan (Poin Persentase)",
        yaxis_title="",
        height=520,
        margin=dict(l=30, r=50, t=20, b=40),
        xaxis=dict(showgrid=True, zeroline=True, zerolinecolor=COLORS["gray_dark"], zerolinewidth=1.5),
    )

    # 2. Figure Stacked Bar Multi-Tahun
    fig_stacked = go.Figure()
    top_items = sub_sectors.groupby("uraian")[metrik_col].sum().abs().sort_values(ascending=False).head(8).index.tolist()

    for item in top_items:
        item_series = sub_sectors[sub_sectors["uraian"] == item].sort_values("tahun")
        color = get_sektor_color_by_name(item)
        fig_stacked.add_trace(
            go.Bar(
                x=item_series["tahun"],
                y=item_series[metrik_col],
                name=item[:25],
                marker_color=color,
                hovertemplate=f"<b>{item[:30]}</b><br>Tahun: %{{x}}<br>SOG: %{{y:+.2f}}%<extra></extra>",
            )
        )

    # Garis pertumbuhan total PDRB
    series_pdrb = sub_kat[sub_kat["kode"] == "PDRB"].sort_values("tahun")
    if not series_pdrb.empty:
        fig_stacked.add_trace(
            go.Scatter(
                x=series_pdrb["tahun"],
                y=series_pdrb[metrik_col],
                mode="lines+markers",
                name="Pertumbuhan Total PDRB",
                line=dict(color=COLORS["accent_dark"], width=3),
                marker=dict(size=8, symbol="diamond"),
                hovertemplate="<b>Total PDRB</b><br>Tahun: %{x}<br>Laju: %{y:+.2f}%<extra></extra>",
            )
        )

    fig_stacked.update_layout(
        barmode="relative",
        yaxis_title="Sumber Pertumbuhan (Poin %)",
        xaxis_title="Tahun",
        xaxis=dict(dtick=1),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        margin=dict(l=40, r=20, t=20, b=90),
    )

    return insight, kpis, fig_diverging, fig_stacked


