from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_kab_kota_list, get_years_list
from utils.analysis import hitung_kontribusi
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import get_sektor_color_by_name, COLORS

kab_kota_list = get_kab_kota_list(exclude_provinsi=False)
years = get_years_list()


def layout():
    return html.Div(
        [
            html.Div(id="kontribusi-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        style={"minWidth": "260px"},
                        children=[
                            html.Label("Wilayah", className="filter-label"),
                            dcc.Dropdown(
                                id="kontribusi-kk",
                                options=[{"label": kk, "value": kk} for kk in kab_kota_list],
                                value=kab_kota_list[0] if kab_kota_list else PROVINSI_LABEL,
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun", className="filter-label"),
                            dcc.Dropdown(
                                id="kontribusi-tahun",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=max(years) if years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Basis Perhitungan", className="filter-label"),
                            dcc.Dropdown(
                                id="kontribusi-basis",
                                options=[
                                    {"label": "ADHB (Struktur Nominal)", "value": "adhb"},
                                    {"label": "ADHK (Struktur Riil)", "value": "adhk"},
                                ],
                                value="adhb",
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="kontribusi-kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1.3fr", "gap": "20px"},
                children=[
                    card("Proporsi Struktur Sektoral (Donut Chart)", dcc.Graph(id="graf-kontribusi-donut")),
                    card("Peringkat Kontribusi 17 Lapangan Usaha (%)", dcc.Graph(id="graf-kontribusi-bar")),
                ],
            ),
        ]
    )


@callback(
    Output("kontribusi-insight-container", "children"),
    Output("kontribusi-kpi-container", "children"),
    Output("graf-kontribusi-donut", "figure"),
    Output("graf-kontribusi-bar", "figure"),
    Input("kontribusi-kk", "value"),
    Input("kontribusi-tahun", "value"),
    Input("kontribusi-basis", "value"),
)
def update_kontribusi(kk, tahun, basis_col):
    df_pdrb = DATA.get("pdrb", None)
    if df_pdrb is None or df_pdrb.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    sub = df_pdrb[(df_pdrb["kab_kota"] == kk) & (df_pdrb["tahun"] == tahun)].copy()
    if sub.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    # Integritas Data: Sektoral kabupaten/kota bersumber dari PDRB ADHK 2010.
    # Level Provinsi memiliki kedua basis resmi (ADHB dan ADHK).
    if kk != PROVINSI_LABEL and (basis_col == "adhb" or sub[basis_col].dropna().empty):
        actual_col = "adhk"
        basis_name = "Harga Konstan Riil (ADHK 2010)"
        note_basis = " (Catatan: Data sektoral resmi BPS kab/kota berbasis ADHK 2010)"
    else:
        actual_col = basis_col
        basis_name = "Harga Berlaku/ADHB" if actual_col == "adhb" else "Harga Konstan/ADHK"
        note_basis = ""

    total_val = sub[actual_col].sum()
    sub["kontribusi_persen"] = (sub[actual_col] / total_val * 100) if total_val > 0 else 0
    sub_sorted = sub.sort_values("kontribusi_persen", ascending=False).reset_index(drop=True)

    # KPI Top 3 Sektor
    top1 = sub_sorted.iloc[0] if len(sub_sorted) > 0 else None
    top2 = sub_sorted.iloc[1] if len(sub_sorted) > 1 else None
    top3 = sub_sorted.iloc[2] if len(sub_sorted) > 2 else None
    top3_share = sub_sorted.head(3)["kontribusi_persen"].sum()
    if kk == "Kabupaten Bintan":
        ind_row = sub_sorted[sub_sorted["kode"] == "C"]
        ind_pct = ind_row["kontribusi_persen"].iloc[0] if not ind_row.empty else 0.0
        insight_content = [
            f"Struktur sektoral Kabupaten Bintan ({tahun}) memperlihatkan corak khas: ditopang kuat oleh sektor ",
            html.Strong(f"{top1['lapangan_usaha']} ({top1['kontribusi_persen']:.1f}%)", className="chat-bubble-highlight"),
            " dan ",
            html.Strong(f"{top2['lapangan_usaha']} ({top2['kontribusi_persen']:.1f}%)", className="chat-bubble-highlight"),
            f". Sektor Industri Manufaktur (C) menyumbang ",
            html.Strong(f"{ind_pct:.1f}%", className="chat-bubble-highlight"),
            ". Hal ini membuktikan bahwa ",
            html.Strong("Bintan BELUM SETARA dengan Batam", className="chat-bubble-highlight"),
            " secara struktur sektoral: Bintan masih berorientasi pada ekonomi pariwisata, jasa, dan maritim-primer, bukan sentra manufaktur padat modal seperti Batam.",
        ]
        insight_title = f"Insight Struktur Sektoral Bintan: Pariwisata & Primer Dominan ({tahun})"
    elif kk == "Kota Batam":
        ind_row = sub_sorted[sub_sorted["kode"] == "C"]
        ind_pct = ind_row["kontribusi_persen"].iloc[0] if not ind_row.empty else 0.0
        insight_content = [
            f"Perekonomian Kota Batam ({tahun}) merupakan perekonomian industri terkonsolidasi. Sektor ",
            html.Strong(f"Industri Pengolahan (C) menyerap {ind_pct:.1f}%", className="chat-bubble-highlight"),
            f" dari seluruh kue ekonomi Batam, didukung oleh jasa modern dan utilitas. Batam memiliki basis industri manufaktur yang sangat matang dan terintegrasi ke rantai pasok global.",
        ]
        insight_title = f"Insight Struktur Sektoral Batam: Basis Manufaktur Kuat ({tahun})"
    else:
        insight_content = [
            f"Pada tahun {tahun}, struktur ekonomi {kk} berbasis {basis_name} memiliki konsentrasi tinggi: 3 sektor teratas menguasai ",
            html.Strong(f"{top3_share:.1f}%", className="chat-bubble-highlight"),
            f" dari total output. Sektor ",
            html.Strong(f"{top1['lapangan_usaha']} memimpin dengan kontribusi {top1['kontribusi_persen']:.1f}%", className="chat-bubble-highlight"),
            f", diikuti {top2['kode']} ({top2['kontribusi_persen']:.1f}%) dan {top3['kode']} ({top3['kontribusi_persen']:.1f}%).",
        ]
        insight_title = f"Insight Struktur Ekonomi {kk} ({tahun})"

    insight = mascot_insight_bubble(
        title=insight_title,
        content=insight_content,
        mascot_src="/assets/maskot_1.webp",
    )

    kpis = [
        kpi_card(
            "Kontributor Utama (#1)",
            f"{top1['kode']} ({top1['kontribusi_persen']:.1f}%)" if top1 is not None else "-",
        ),
        kpi_card(
            "Kontributor Kedua (#2)",
            f"{top2['kode']} ({top2['kontribusi_persen']:.1f}%)" if top2 is not None else "-",
        ),
        kpi_card(
            "Kontributor Ketiga (#3)",
            f"{top3['kode']} ({top3['kontribusi_persen']:.1f}%)" if top3 is not None else "-",
        ),
        kpi_card(
            "Konsentrasi Top 3 Sektor",
            f"{top3_share:.1f}%",
        ),
    ]

    # Donut Chart
    colors_donut = [get_sektor_color_by_name(lu) for lu in sub_sorted["lapangan_usaha"]]
    # Singkat label untuk donut
    short_donut_labels = [
        lu[:30] + "..." if len(lu) > 30 else lu for lu in sub_sorted["lapangan_usaha"]
    ]

    fig_donut = go.Figure(
        go.Pie(
            labels=short_donut_labels,
            values=sub_sorted[basis_col],
            hole=0.48,
            marker=dict(colors=colors_donut),
            textinfo="percent",
            hoverinfo="label+percent+value",
            hovertemplate="<b>%{label}</b><br>Nominal: Rp %{value:,.1f} M<br>Pangsa: %{percent}<extra></extra>",
        )
    )
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[
            dict(
                text=f"Total<br><b>Rp {total_val:,.0f} M</b>",
                x=0.5,
                y=0.5,
                font_size=13,
                showarrow=False,
            )
        ],
    )

    # Bar Chart Ranking
    bar_data = sub_sorted.sort_values("kontribusi_persen", ascending=True)
    colors_bar = [get_sektor_color_by_name(lu) for lu in bar_data["lapangan_usaha"]]
    short_bar_labels = [
        lu[:32] + "..." if len(lu) > 32 else lu for lu in bar_data["lapangan_usaha"]
    ]

    fig_bar = go.Figure(
        go.Bar(
            y=short_bar_labels,
            x=bar_data["kontribusi_persen"],
            orientation="h",
            marker=dict(color=colors_bar),
            text=[f"{v:.2f}%" for v in bar_data["kontribusi_persen"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Kontribusi: %{x:.2f}%<extra></extra>",
        )
    )
    fig_bar.update_layout(
        xaxis_title="Kontribusi (%)",
        yaxis_title="",
        height=540,
        margin=dict(l=30, r=50, t=20, b=40),
        xaxis=dict(showgrid=True),
    )

    return insight, kpis, fig_donut, fig_bar


