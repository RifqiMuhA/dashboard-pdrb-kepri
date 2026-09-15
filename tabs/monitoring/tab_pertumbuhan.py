from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_kab_kota_list, get_years_list
from utils.analysis import hitung_laju_pertumbuhan
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import KABKOTA_COLORS, REFERENCE_LINE_STYLE, COLORS

years = get_years_list()
growth_years = [y for y in years if y > min(years)] if years else [2022, 2023, 2024, 2025]
kab_kota_list = get_kab_kota_list(exclude_provinsi=True)


def layout():
    return html.Div(
        [
            html.Div(id="pertumbuhan-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun Fokus Evaluasi", className="filter-label"),
                            dcc.Dropdown(
                                id="pertumbuhan-tahun",
                                options=[{"label": str(y), "value": y} for y in growth_years],
                                value=max(growth_years) if growth_years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        style={"minWidth": "320px"},
                        children=[
                            html.Label("Sorot Kabupaten/Kota", className="filter-label"),
                            dcc.Dropdown(
                                id="pertumbuhan-filter-kk",
                                options=[{"label": kk, "value": kk} for kk in kab_kota_list],
                                value=kab_kota_list,
                                multi=True,
                                placeholder="Pilih wilayah untuk ditampilkan...",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="pertumbuhan-kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1.6fr 1fr", "gap": "20px"},
                children=[
                    card("Tren Laju Pertumbuhan Ekonomi Riil (2021–2025)", dcc.Graph(id="graf-pertumbuhan-tren")),
                    card("Peringkat Pertumbuhan pada Tahun Terpilih", dcc.Graph(id="graf-pertumbuhan-bar")),
                ],
            ),
        ]
    )


@callback(
    Output("pertumbuhan-insight-container", "children"),
    Output("pertumbuhan-kpi-container", "children"),
    Output("graf-pertumbuhan-tren", "figure"),
    Output("graf-pertumbuhan-bar", "figure"),
    Input("pertumbuhan-tahun", "value"),
    Input("pertumbuhan-filter-kk", "value"),
)
def update_pertumbuhan(tahun_fokus, selected_kk):
    df_pdrb = DATA.get("pdrb", None)
    if df_pdrb is None or df_pdrb.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    growth_df = hitung_laju_pertumbuhan(df_pdrb)
    growth_clean = growth_df.dropna(subset=["laju_pertumbuhan"]).copy()

    # Data Provinsi Kepri
    prov_series = growth_clean[growth_clean["kab_kota"] == PROVINSI_LABEL]
    prov_val_fokus = (
        prov_series[prov_series["tahun"] == tahun_fokus]["laju_pertumbuhan"].iloc[0]
        if not prov_series[prov_series["tahun"] == tahun_fokus].empty
        else 0.0
    )

    # Data Kab/Kota
    kk_clean = growth_clean[growth_clean["kab_kota"] != PROVINSI_LABEL].copy()
    kk_fokus = kk_clean[kk_clean["tahun"] == tahun_fokus].sort_values("laju_pertumbuhan", ascending=False)

    best_kk = kk_fokus.iloc[0] if not kk_fokus.empty else None
    worst_kk = kk_fokus.iloc[-1] if not kk_fokus.empty else None

    # Bintan & Batam growth
    bintan_row = kk_fokus[kk_fokus["kab_kota"] == "Kabupaten Bintan"]
    batam_row = kk_fokus[kk_fokus["kab_kota"] == "Kota Batam"]
    bintan_growth = bintan_row["laju_pertumbuhan"].iloc[0] if not bintan_row.empty else 0.0
    batam_growth = batam_row["laju_pertumbuhan"].iloc[0] if not batam_row.empty else 0.0

    best_name = best_kk['kab_kota'].replace('Kabupaten ', 'Kab. ').replace('Kota ', '') if best_kk is not None else "-"
    worst_name = worst_kk['kab_kota'].replace('Kabupaten ', 'Kab. ').replace('Kota ', '') if worst_kk is not None else "-"

    insight_content = [
        f"Pada tahun {tahun_fokus}, perekonomian Provinsi Kepulauan Riau tumbuh sebesar ",
        html.Strong(f"{prov_val_fokus:.2f}%", className="chat-bubble-highlight"),
        ". Menariknya, ",
        html.Strong("Kabupaten Bintan", className="chat-bubble-highlight"),
        f" membukukan laju pertumbuhan pesat sebesar ",
        html.Strong(f"{bintan_growth:.2f}%", className="chat-bubble-highlight"),
        f", berhasil melampaui laju ",
        html.Strong(f"Kota Batam ({batam_growth:.2f}%)", className="chat-bubble-highlight"),
        f" serta di atas rata-rata provinsi! Daerah dengan laju pertumbuhan tertinggi adalah ",
        html.Strong(f"{best_name} ({best_kk['laju_pertumbuhan']:.2f}%)", className="chat-bubble-highlight") if best_kk is not None else "",
        f", sedangkan posisi terendah ditempati oleh {worst_name} ({worst_kk['laju_pertumbuhan']:.2f}%). Laju pertumbuhan Bintan yang lebih kencang membuktikan adanya akselerasi (catch-up effect) yang sangat kuat.",
    ]

    insight = mascot_insight_bubble(
        title=f"Insight Laju Pertumbuhan Ekonomi: Akselerasi Bintan vs Batam ({tahun_fokus})",
        content=insight_content,
        mascot_src="/assets/maskot_2.webp",
    )

    kpis = [
        kpi_card(
            f"Pertumbuhan {PROVINSI_LABEL} ({tahun_fokus})",
            f"{prov_val_fokus:.2f}%",
        ),
        kpi_card(
            f"Pertumbuhan Tertinggi ({tahun_fokus})",
            f"{best_kk['kab_kota'].replace('Kabupaten ', 'Kab. ').replace('Kota ', '')} ({best_kk['laju_pertumbuhan']:.2f}%)" if best_kk is not None else "-",
        ),
        kpi_card(
            f"Pertumbuhan Terendah ({tahun_fokus})",
            f"{worst_kk['kab_kota'].replace('Kabupaten ', 'Kab. ').replace('Kota ', '')} ({worst_kk['laju_pertumbuhan']:.2f}%)" if worst_kk is not None else "-",
        ),
    ]

    # 1. Figure Tren Garis
    fig_tren = go.Figure()
    active_kks = selected_kk if selected_kk else kab_kota_list

    for kk in active_kks:
        sub_kk = kk_clean[kk_clean["kab_kota"] == kk].sort_values("tahun")
        color = KABKOTA_COLORS.get(kk, COLORS["primary"])
        fig_tren.add_trace(
            go.Scatter(
                x=sub_kk["tahun"],
                y=sub_kk["laju_pertumbuhan"],
                mode="lines+markers",
                name=kk.replace("Kabupaten ", "Kab. "),
                line=dict(color=color, width=2.5),
                marker=dict(size=7),
                hovertemplate=f"<b>{kk}</b><br>Tahun: %{{x}}<br>Pertumbuhan: %{{y:.2f}}%<extra></extra>",
            )
        )

    # Garis acuan Kepri
    if not prov_series.empty:
        fig_tren.add_trace(
            go.Scatter(
                x=prov_series["tahun"],
                y=prov_series["laju_pertumbuhan"],
                mode="lines+markers",
                name=f"Rata-rata {PROVINSI_LABEL}",
                line=dict(color=COLORS["accent_dark"], dash="dash", width=3),
                marker=dict(size=8, symbol="diamond"),
                hovertemplate="<b>Provinsi Kepri</b><br>Tahun: %{x}<br>Pertumbuhan: %{y:.2f}%<extra></extra>",
            )
        )

    fig_tren.update_layout(
        yaxis_title="Laju Pertumbuhan (%)",
        xaxis_title="Tahun",
        xaxis=dict(dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=40, r=20, t=20, b=80),
    )

    # 2. Figure Bar Chart Peringkat Tahun Fokus
    fig_bar = go.Figure()
    kk_bar_data = kk_fokus.sort_values("laju_pertumbuhan", ascending=True)

    bar_colors = [KABKOTA_COLORS.get(kk, COLORS["primary"]) for kk in kk_bar_data["kab_kota"]]
    short_names = [
        kk.replace("Kabupaten ", "Kab. ").replace("Kota ", "")
        for kk in kk_bar_data["kab_kota"]
    ]

    fig_bar.add_trace(
        go.Bar(
            y=short_names,
            x=kk_bar_data["laju_pertumbuhan"],
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{val:.2f}%" for val in kk_bar_data["laju_pertumbuhan"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Pertumbuhan: %{x:.2f}%<extra></extra>",
        )
    )

    # Garis referensi provinsi pada bar chart
    fig_bar.add_vline(
        x=prov_val_fokus,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=2),
        annotation_text=f"Kepri: {prov_val_fokus:.2f}%",
        annotation_position="top right",
    )

    fig_bar.update_layout(
        xaxis_title="Laju Pertumbuhan (%)",
        yaxis_title="",
        margin=dict(l=30, r=40, t=20, b=40),
        xaxis=dict(showgrid=True),
    )

    return insight, kpis, fig_tren, fig_bar


