from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list, get_kab_kota_list
from utils.components import card, kpi_card, mascot_insight_bubble
from theme import KABKOTA_COLORS, REFERENCE_LINE_STYLE, COLORS

years = get_years_list()
kab_kota_list = get_kab_kota_list(exclude_provinsi=True)


def layout():
    return html.Div(
        [
            html.Div(id="perkapita-insight-container"),
            html.Div(
                className="filter-row",
                children=[
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Basis Harga", className="filter-label"),
                            dcc.Dropdown(
                                id="perkapita-tipe",
                                options=[
                                    {"label": "ADHB (Harga Berlaku)", "value": "perkapita_adhb_juta"},
                                    {"label": "ADHK (Harga Konstan 2010)", "value": "perkapita_adhk_juta"},
                                ],
                                value="perkapita_adhb_juta",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Tahun", className="filter-label"),
                            dcc.Dropdown(
                                id="perkapita-tahun",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=max(years) if years else 2025,
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="perkapita-kpi-container",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1.2fr 1.4fr", "gap": "20px"},
                children=[
                    card("Perbandingan PDRB Perkapita per Wilayah", dcc.Graph(id="graf-perkapita-bar")),
                    card("Tren Pertumbuhan PDRB Perkapita (2021–2025)", dcc.Graph(id="graf-perkapita-tren")),
                ],
            ),
        ]
    )


@callback(
    Output("perkapita-insight-container", "children"),
    Output("perkapita-kpi-container", "children"),
    Output("graf-perkapita-bar", "figure"),
    Output("graf-perkapita-tren", "figure"),
    Input("perkapita-tipe", "value"),
    Input("perkapita-tahun", "value"),
)
def update_perkapita(tipe_col, tahun):
    df_pk = DATA.get("perkapita", None)
    if df_pk is None or df_pk.empty:
        return html.Div(), [], go.Figure(), go.Figure()

    satuan_label = "Juta Rp/jiwa"
    basis_name = "ADHB (Harga Berlaku)" if "adhb" in tipe_col else "ADHK (Harga Konstan)"

    # Filter tahun terpilih
    sub_tahun = df_pk[df_pk["tahun"] == tahun]
    prov_row = sub_tahun[sub_tahun["kab_kota"] == PROVINSI_LABEL]
    prov_val = prov_row[tipe_col].iloc[0] if not prov_row.empty else 0.0

    kk_sub = sub_tahun[sub_tahun["kab_kota"] != PROVINSI_LABEL].sort_values(tipe_col, ascending=True)

    # Nilai Bintan vs Batam
    bintan_row = sub_tahun[sub_tahun["kab_kota"] == "Kabupaten Bintan"]
    batam_row = sub_tahun[sub_tahun["kab_kota"] == "Kota Batam"]
    bintan_val = bintan_row[tipe_col].iloc[0] if not bintan_row.empty else 0.0
    batam_val = batam_row[tipe_col].iloc[0] if not batam_row.empty else 0.0
    rasio_bintan_batam = (bintan_val / batam_val * 100) if batam_val > 0 else 0.0

    insight_content = [
        f"Pada tahun {tahun}, indikator kesejahteraan per kapita ({basis_name}) menunjukkan bahwa ",
        html.Strong("Kabupaten Bintan telah SETARA secara nominal dengan Kota Batam!", className="chat-bubble-highlight"),
        f" PDRB perkapita Bintan menyentuh ",
        html.Strong(f"Rp {bintan_val:,.1f} Jt/jiwa", className="chat-bubble-highlight"),
        f", setara dengan rasio ",
        html.Strong(f"{rasio_bintan_batam:.1f}%", className="chat-bubble-highlight"),
        f" dari Batam (Rp {batam_val:,.1f} Jt/jiwa), keduanya melampaui rata-rata Kepri (Rp {prov_val:,.1f} Jt). Meskipun demikian, kesetaraan nominal ini tidak berarti kesetaraan struktur sektoral: Bintan mengandalkan pariwisata beroutput tinggi dan populasi ramping, sementara Batam bertumpu pada skala pabrikasi industri padat modal.",
    ]

    insight = mascot_insight_bubble(
        title=f"Insight Evaluasi Kesetaraan: Bintan vs Batam ({tahun})",
        content=insight_content,
        mascot_src="/assets/maskot_2.webp",
    )

    kpis = [
        kpi_card(
            f"Rata-rata {PROVINSI_LABEL} ({tahun})",
            f"Rp {prov_val:,.1f} Jt",
        ),
        kpi_card(
            f"PDRB Perkapita Bintan ({tahun})",
            f"Rp {bintan_val:,.1f} Jt",
        ),
        kpi_card(
            f"PDRB Perkapita Batam ({tahun})",
            f"Rp {batam_val:,.1f} Jt",
        ),
        kpi_card(
            "Rasio Kesetaraan Bintan / Batam",
            f"{rasio_bintan_batam:.1f}%",
        ),
    ]

    # 1. Bar Chart Komparasi per Kab/Kota
    colors_bar = [KABKOTA_COLORS.get(kk, COLORS["primary"]) for kk in kk_sub["kab_kota"]]
    labels_bar = [
        kk.replace("Kabupaten ", "Kab. ").replace("Kota ", "")
        for kk in kk_sub["kab_kota"]
    ]

    fig_bar = go.Figure(
        go.Bar(
            y=labels_bar,
            x=kk_sub[tipe_col],
            orientation="h",
            marker=dict(color=colors_bar),
            text=[f"Rp {v:,.1f} Jt" for v in kk_sub[tipe_col]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>PDRB Perkapita: Rp %{x:,.2f} Juta/jiwa<extra></extra>",
        )
    )
    fig_bar.add_vline(
        x=prov_val,
        line=dict(color=COLORS["accent_dark"], dash="dash", width=2),
        annotation_text=f"Rata-rata Kepri: Rp {prov_val:,.1f} Jt",
        annotation_position="top right",
    )
    fig_bar.update_layout(
        xaxis_title=f"PDRB Perkapita ({satuan_label})",
        yaxis_title="",
        margin=dict(l=30, r=40, t=20, b=40),
        xaxis=dict(showgrid=True),
    )

    # 2. Line Chart Tren 2021-2025
    fig_tren = go.Figure()
    for kk in kab_kota_list:
        sub_kk = df_pk[df_pk["kab_kota"] == kk].sort_values("tahun")
        color = KABKOTA_COLORS.get(kk, COLORS["primary"])
        # Berikan penekanan visual pada Bintan & Batam
        is_highlight = kk in ["Kabupaten Bintan", "Kota Batam"]
        fig_tren.add_trace(
            go.Scatter(
                x=sub_kk["tahun"],
                y=sub_kk[tipe_col],
                mode="lines+markers",
                name=kk.replace("Kabupaten ", "Kab. "),
                line=dict(color=color, width=3.5 if is_highlight else 1.8),
                marker=dict(size=8 if is_highlight else 5),
                hovertemplate=f"<b>{kk}</b><br>Tahun: %{{x}}<br>Perkapita: Rp %{{y:,.2f}} Juta<extra></extra>",
            )
        )

    # Garis acuan Kepri di tren
    sub_prov = df_pk[df_pk["kab_kota"] == PROVINSI_LABEL].sort_values("tahun")
    if not sub_prov.empty:
        fig_tren.add_trace(
            go.Scatter(
                x=sub_prov["tahun"],
                y=sub_prov[tipe_col],
                mode="lines+markers",
                name="Rata-rata Kepri",
                line=dict(color=COLORS["accent_dark"], dash="dash", width=2.5),
                marker=dict(size=7, symbol="diamond"),
                hovertemplate="<b>Rata-rata Kepri</b><br>Tahun: %{x}<br>Perkapita: Rp %{y:,.2f} Juta<extra></extra>",
            )
        )

    fig_tren.update_layout(
        xaxis_title="Tahun",
        yaxis_title=f"PDRB Perkapita ({satuan_label})",
        xaxis=dict(dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=40, r=20, t=20, b=80),
    )

    return insight, kpis, fig_bar, fig_tren


