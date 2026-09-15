import pandas as pd
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_kab_kota_list, get_years_list
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import COLORS

years = get_years_list()
kab_kota_list = get_kab_kota_list(exclude_provinsi=False)
wilayah_options = [{"label": "Semua Kabupaten/Kota", "value": "ALL"}] + [
    {"label": kk, "value": kk} for kk in kab_kota_list
]


def layout():
    return html.Div(
        [
            html.Div(id="nominal-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun", className="filter-label"),
                            dcc.Dropdown(
                                id="nominal-tahun",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=max(years) if years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        style={"minWidth": "280px"},
                        children=[
                            html.Label("Cakupan Wilayah", className="filter-label"),
                            dcc.Dropdown(
                                id="nominal-wilayah",
                                options=wilayah_options,
                                value="ALL",
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="nominal-kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
            ),
            card("Perbandingan Nilai Nominal PDRB ADHB vs ADHK", dcc.Graph(id="graf-nominal")),
        ]
    )


@callback(
    Output("nominal-insight-container", "children"),
    Output("nominal-kpi-container", "children"),
    Output("graf-nominal", "figure"),
    Input("nominal-tahun", "value"),
    Input("nominal-wilayah", "value"),
)
def update_nominal(tahun, wilayah):
    df = DATA.get("pdrb", None)
    if df is None or df.empty:
        return html.Div(), [], go.Figure()

    fig = go.Figure()

    df_pk = DATA.get("perkapita", None)
    df_pop = DATA.get("penduduk", None)

    if wilayah == "ALL":
        sub = df[(df["kab_kota"] != PROVINSI_LABEL) & (df["tahun"] == tahun)]
        agg = sub.groupby("kab_kota", as_index=False)["adhk"].sum()

        # Hitung Total PDRB ADHB agregat resmi via (Perkapita ADHB * Penduduk)
        if df_pk is not None and df_pop is not None:
            m = pd.merge(
                df_pk[df_pk["tahun"] == tahun],
                df_pop[df_pop["tahun"] == tahun],
                on=["kab_kota", "tahun"],
            )
            m["adhb"] = (m["perkapita_adhb_ribu"] * m["jumlah_penduduk"]) / 1e6
            agg = pd.merge(agg, m[["kab_kota", "adhb"]], on="kab_kota", how="left")
        else:
            agg["adhb"] = 0.0

        agg = agg.sort_values("adhk", ascending=False)

        total_adhb = agg["adhb"].sum()
        total_adhk = agg["adhk"].sum()
        deflator = (total_adhb / total_adhk * 100) if total_adhk > 0 else 100

        # Data Bintan vs Batam
        batam_row = agg[agg["kab_kota"] == "Kota Batam"]
        bintan_row = agg[agg["kab_kota"] == "Kabupaten Bintan"]
        batam_adhk = batam_row["adhk"].iloc[0] if not batam_row.empty else 0
        bintan_adhk = bintan_row["adhk"].iloc[0] if not bintan_row.empty else 0
        batam_pct = (batam_adhk / total_adhk * 100) if total_adhk > 0 else 0
        bintan_pct = (bintan_adhk / total_adhk * 100) if total_adhk > 0 else 0
        ratio_scale = (batam_adhk / bintan_adhk) if bintan_adhk > 0 else 0

        insight_content = [
            f"Pada tahun {tahun}, total kue ekonomi riil (ADHK 2010) seluruh kabupaten/kota di Kepri mencapai ",
            html.Strong(f"Rp {total_adhk:,.1f} Miliar", className="chat-bubble-highlight"),
            " (dengan estimasi nominal agregat ADHB mencapai ",
            html.Strong(f"Rp {total_adhb:,.1f} Miliar", className="chat-bubble-highlight"),
            "). ",
            html.Strong("Kota Batam", className="chat-bubble-highlight"),
            f" mendominasi secara absolut dengan pangsa ",
            html.Strong(f"{batam_pct:.1f}%", className="chat-bubble-highlight"),
            f", sementara ",
            html.Strong("Kabupaten Bintan", className="chat-bubble-highlight"),
            f" menyumbang ",
            html.Strong(f"{bintan_pct:.1f}%", className="chat-bubble-highlight"),
            f". Skala agregat ekonomi Batam sekitar {ratio_scale:.1f}x lipat dari Bintan, menegaskan bahwa secara volume dan kapasitas total, Bintan belum setara dengan Batam.",
        ]
        insight = mascot_insight_bubble(
            title=f"Insight Skala Nominal & Dominasi Ekonomi Daerah ({tahun})",
            content=insight_content,
            mascot_src="/assets/maskot_1.webp",
        )

        kpis = [
            kpi_card(f"Total ADHK Kab/Kota ({tahun})", f"Rp {total_adhk:,.1f} M"),
            kpi_card(f"Total ADHB Agregat ({tahun})", f"Rp {total_adhb:,.1f} M"),
            kpi_card("Indeks Deflator Agregat", f"{deflator:.2f}"),
        ]

        fig.add_trace(
            go.Bar(
                x=agg["kab_kota"],
                y=agg["adhk"],
                name="ADHK (Harga Konstan 2010)",
                marker_color=COLORS["accent"],
                hovertemplate="<b>%{x}</b><br>ADHK: Rp %{y:,.1f} M<extra></extra>",
            )
        )
        fig.add_trace(
            go.Bar(
                x=agg["kab_kota"],
                y=agg["adhb"],
                name="ADHB (Harga Berlaku Agregat)",
                marker_color=COLORS["primary"],
                hovertemplate="<b>%{x}</b><br>ADHB: Rp %{y:,.1f} M<extra></extra>",
            )
        )
        fig.update_layout(
            barmode="group",
            yaxis_title="Miliar Rupiah",
            xaxis_title="Kabupaten / Kota",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    else:
        sub = df[(df["kab_kota"] == wilayah) & (df["tahun"] == tahun)]
        agg = sub.sort_values("adhk", ascending=True)

        total_adhk = agg["adhk"].sum()

        # Ambil PDRB perkapita dan total ADHB agregat resmi
        pk_adhk = 0.0
        pk_adhb = 0.0
        total_adhb = 0.0
        if df_pk is not None:
            pk_row = df_pk[(df_pk["kab_kota"] == wilayah) & (df_pk["tahun"] == tahun)]
            if not pk_row.empty:
                pk_adhk = pk_row["perkapita_adhk_juta"].iloc[0]
                pk_adhb = pk_row["perkapita_adhb_juta"].iloc[0]

        if wilayah == PROVINSI_LABEL:
            total_adhb = agg["adhb"].sum()
        else:
            if df_pop is not None:
                pop_row = df_pop[(df_pop["kab_kota"] == wilayah) & (df_pop["tahun"] == tahun)]
                if not pop_row.empty:
                    pop_val = pop_row["jumlah_penduduk"].iloc[0]
                    total_adhb = (pk_adhb * 1000 * pop_val) / 1e6

        deflator = (total_adhb / total_adhk * 100) if total_adhk > 0 else 100

        top_row = agg.iloc[-1]
        top_adhk = top_row["adhk"]
        top_share = (top_adhk / total_adhk * 100) if total_adhk > 0 else 0

        insight_content = [
            f"PDRB riil {wilayah} pada tahun {tahun} tercatat sebesar ",
            html.Strong(f"Rp {total_adhk:,.1f} Miliar (ADHK 2010)", className="chat-bubble-highlight"),
            f" dengan estimasi nilai nominal agregat ",
            html.Strong(f"Rp {total_adhb:,.1f} Miliar (ADHB)", className="chat-bubble-highlight"),
            f". PDRB per kapita berada di level ",
            html.Strong(f"Rp {pk_adhk:.1f} Jt (ADHK)", className="chat-bubble-highlight"),
            f" dan ",
            html.Strong(f"Rp {pk_adhb:.1f} Jt (ADHB)", className="chat-bubble-highlight"),
            f". Sektor penopang riil terbesar adalah ",
            html.Strong(f"{top_row['lapangan_usaha']}", className="chat-bubble-highlight"),
            f" yang menyumbang ",
            html.Strong(f"Rp {top_adhk:,.1f} Miliar ({top_share:.1f}%)", className="chat-bubble-highlight"),
            ".",
        ]
        insight = mascot_insight_bubble(
            title=f"Insight Profil Output {wilayah} ({tahun})",
            content=insight_content,
            mascot_src="/assets/maskot_1.webp",
        )

        kpis = [
            kpi_card(f"PDRB Riil ADHK ({tahun})", f"Rp {total_adhk:,.1f} M"),
            kpi_card(f"PDRB Perkapita Riil", f"Rp {pk_adhk:.1f} Jt"),
            kpi_card(f"PDRB Perkapita ADHB", f"Rp {pk_adhb:.1f} Jt"),
            kpi_card(f"Sektor Utama ({top_row['kode']})", f"{top_share:.1f}%"),
        ]

        clean_labels = [lu[:35] + "..." if len(lu) > 35 else lu for lu in agg["lapangan_usaha"]]

        if wilayah == PROVINSI_LABEL:
            fig.add_trace(
                go.Bar(
                    y=clean_labels,
                    x=agg["adhb"],
                    orientation="h",
                    name="ADHB (Harga Berlaku)",
                    marker_color=COLORS["primary"],
                    hovertemplate="<b>%{y}</b><br>ADHB: Rp %{x:,.1f} M<extra></extra>",
                )
            )
            fig.add_trace(
                go.Bar(
                    y=clean_labels,
                    x=agg["adhk"],
                    orientation="h",
                    name="ADHK (Harga Konstan 2010)",
                    marker_color=COLORS["accent"],
                    hovertemplate="<b>%{y}</b><br>ADHK: Rp %{x:,.1f} M<extra></extra>",
                )
            )
            fig.update_layout(barmode="group")
        else:
            fig.add_trace(
                go.Bar(
                    y=clean_labels,
                    x=agg["adhk"],
                    orientation="h",
                    name="ADHK (Harga Konstan 2010)",
                    marker_color=COLORS["primary"],
                    text=[f"Rp {v:,.1f} M" for v in agg["adhk"]],
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>ADHK: Rp %{x:,.1f} M<extra></extra>",
                )
            )

        fig.update_layout(
            xaxis_title="Miliar Rupiah (ADHK 2010)",
            yaxis_title="",
            height=580,
            margin=dict(l=20, r=60, t=30, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

    return insight, kpis, fig


