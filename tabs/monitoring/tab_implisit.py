from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, get_years_list
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import get_sektor_color_by_name, COLORS

years = get_years_list()


def layout():
    df_impl = DATA.get("implisit", None)
    lu_options = []
    if df_impl is not None and not df_impl.empty:
        utama_df = df_impl[df_impl["is_utama"] == True]
        unique_lu = utama_df["lapangan_usaha"].unique().tolist()
        # Letakkan PDRB di paling atas
        if "Produk Domestik Regional Bruto (PDRB)" in unique_lu:
            unique_lu.remove("Produk Domestik Regional Bruto (PDRB)")
            unique_lu.insert(0, "Produk Domestik Regional Bruto (PDRB)")
        lu_options = [{"label": lu, "value": lu} for lu in unique_lu]

    return html.Div(
        [
            html.Div(id="implisit-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        style={"minWidth": "360px"},
                        children=[
                            html.Label("Sektor Lapangan Usaha", className="filter-label"),
                            dcc.Dropdown(
                                id="implisit-lu",
                                options=lu_options,
                                value=(
                                    "Produk Domestik Regional Bruto (PDRB)"
                                    if lu_options
                                    else ""
                                ),
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun Fokus Evaluasi", className="filter-label"),
                            dcc.Dropdown(
                                id="implisit-tahun",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=max(years) if years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="implisit-kpi-container",
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
                        "Tren Indeks Deflator & Laju Inflasi Implisit Sektor Terpilih",
                        dcc.Graph(id="graf-implisit-dual"),
                    ),
                    card(
                        "Perbandingan Laju Inflasi Implisit Antar 17 Sektor (Tahun Fokus)",
                        dcc.Graph(id="graf-implisit-bar"),
                    ),
                ],
            ),
        ]
    )


@callback(
    Output("implisit-insight-container", "children"),
    Output("implisit-kpi-container", "children"),
    Output("graf-implisit-dual", "figure"),
    Output("graf-implisit-bar", "figure"),
    Input("implisit-lu", "value"),
    Input("implisit-tahun", "value"),
)
def update_implisit(selected_lu, tahun_fokus):
    df_impl = DATA.get("implisit", None)
    if df_impl is None or df_impl.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    # 1. Data Sektor Terpilih untuk Dual Axis
    sub_lu = df_impl[df_impl["lapangan_usaha"] == selected_lu].sort_values("tahun")
    val_fokus_row = sub_lu[sub_lu["tahun"] == tahun_fokus]
    indeks_val = val_fokus_row["indeks_implisit"].iloc[0] if not val_fokus_row.empty else 0.0
    laju_val = val_fokus_row["laju_implisit"].iloc[0] if not val_fokus_row.empty else 0.0

    # 2. Data Komparasi Seluruh 17 Sektor pada Tahun Fokus
    all_17 = df_impl[
        (df_impl["is_utama"] == True)
        & (~df_impl["kode"].isin(["TOTAL", "TOTAL_NON_MIGAS"]))
        & (df_impl["tahun"] == tahun_fokus)
    ].sort_values("laju_implisit", ascending=True)

    highest_inf = all_17.iloc[-1] if not all_17.empty else None
    lowest_inf = all_17.iloc[0] if not all_17.empty else None

    high_name = f"{highest_inf['lapangan_usaha']} ({highest_inf['kode']})" if highest_inf is not None else "-"
    low_name = f"{lowest_inf['lapangan_usaha']} ({lowest_inf['kode']})" if lowest_inf is not None else "-"

    insight_content = [
        f"Pada tahun {tahun_fokus}, indeks implisit untuk ",
        html.Strong(f"{selected_lu}", className="chat-bubble-highlight"),
        f" berada pada level ",
        html.Strong(f"{indeks_val:.2f} poin", className="chat-bubble-highlight"),
        f" dengan laju inflasi PDRB sebesar ",
        html.Strong(f"{laju_val:+.2f}%", className="chat-bubble-highlight"),
        f". Di antara 17 lapangan usaha, lonjakan inflasi implisit tertinggi dialami oleh sektor ",
        html.Strong(f"{high_name} ({highest_inf['laju_implisit']:+.2f}%)", className="chat-bubble-highlight") if highest_inf is not None else "",
        f", sedangkan tekanan harga paling terkendali/terkoreksi berada di sektor ",
        html.Strong(f"{low_name} ({lowest_inf['laju_implisit']:+.2f}%)", className="chat-bubble-highlight") if lowest_inf is not None else "",
        ". Dinamika ini merefleksikan pergeseran tingkat harga output produsen di tingkat wilayah.",
    ]

    insight = mascot_insight_bubble(
        title=f"Insight Deflator PDRB & Tekanan Inflasi Sektoral ({tahun_fokus})",
        content=insight_content,
        mascot_src="/assets/maskot_2.webp",
    )

    kpis = [
        kpi_card(
            f"Indeks Implisit ({tahun_fokus})",
            f"{indeks_val:.2f}",
        ),
        kpi_card(
            f"Laju Inflasi Implisit ({tahun_fokus})",
            f"{laju_val:+.2f}%",
        ),
        kpi_card(
            f"Inflasi Tertinggi ({tahun_fokus})",
            f"{highest_inf['kode']} ({highest_inf['laju_implisit']:+.2f}%)" if highest_inf is not None else "-",
        ),
        kpi_card(
            f"Inflasi Terendah ({tahun_fokus})",
            f"{lowest_inf['kode']} ({lowest_inf['laju_implisit']:+.2f}%)" if lowest_inf is not None else "-",
        ),
    ]

    # Figure Dual Axis
    fig_dual = go.Figure()
    fig_dual.add_trace(
        go.Scatter(
            x=sub_lu["tahun"],
            y=sub_lu["indeks_implisit"],
            mode="lines+markers",
            name="Indeks Implisit (2010=100)",
            line=dict(color=COLORS["primary"], width=3),
            marker=dict(size=8),
            hovertemplate="<b>Indeks Deflator</b><br>Tahun: %{x}<br>Indeks: %{y:.2f}<extra></extra>",
        )
    )
    fig_dual.add_trace(
        go.Scatter(
            x=sub_lu["tahun"],
            y=sub_lu["laju_implisit"],
            mode="lines+markers",
            name="Laju Implisit (%)",
            line=dict(color=COLORS["accent"], width=3, dash="dot"),
            marker=dict(size=8, symbol="square"),
            yaxis="y2",
            hovertemplate="<b>Laju Inflasi PDRB</b><br>Tahun: %{x}<br>Laju: %{y:+.2f}%<extra></extra>",
        )
    )
    fig_dual.update_layout(
        xaxis=dict(title="Tahun", dtick=1),
        yaxis=dict(title="Indeks Implisit (Poin)", showgrid=True),
        yaxis2=dict(
            title="Laju Pertumbuhan (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=True,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=20, b=80),
    )

    # Figure Bar Chart 17 Sektor
    bar_colors = [get_sektor_color_by_name(lu) for lu in all_17["lapangan_usaha"]]
    short_labels = [
        lu[:30] + "..." if len(lu) > 30 else lu
        for lu in all_17["lapangan_usaha"]
    ]

    fig_bar = go.Figure(
        go.Bar(
            y=short_labels,
            x=all_17["laju_implisit"],
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{v:+.2f}%" for v in all_17["laju_implisit"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Laju Inflasi: %{x:+.2f}%<extra></extra>",
        )
    )
    fig_bar.update_layout(
        xaxis_title="Laju Indeks Implisit (%)",
        yaxis_title="",
        height=520,
        margin=dict(l=30, r=50, t=20, b=40),
        xaxis=dict(showgrid=True, zeroline=True, zerolinecolor=COLORS["gray_dark"]),
    )

    return insight, kpis, fig_dual, fig_bar

