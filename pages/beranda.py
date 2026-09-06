import dash
from dash import html, dcc, callback, Output, Input
import plotly.express as px

from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list
from utils.analysis import hitung_laju_pertumbuhan, hitung_pdrb_perkapita
from theme import COLORS

dash.register_page(__name__, path="/", name="Beranda")

years = get_years_list()
latest_year = max(years) if years else 2025

layout = html.Div(
    [
        # TOP ROW
        html.Div(id="home-top-row-container", className="home-top-row"),
        
        # BOTTOM ROW
        html.Div(
            className="home-bottom-row",
            children=[
                html.Div(
                    className="home-chart-card",
                    children=[
                        dcc.Tabs(
                            id="home-chart-tabs",
                            className="custom-tabs",
                            value="adhb",
                            children=[
                                dcc.Tab(label="PDRB ADHB", value="adhb", className="tab", selected_className="tab--selected"),
                                dcc.Tab(label="PDRB ADHK", value="adhk", className="tab", selected_className="tab--selected"),
                            ],
                            style={"width": "300px", "marginBottom": "20px"}
                        ),
                        dcc.Graph(id="home-main-chart", style={"height": "320px", "margin": "0"})
                    ]
                ),
                html.Div(
                    className="home-list-card",
                    id="home-list-container"
                )
            ]
        )
    ]
)


@callback(Output("home-top-row-container", "children"), Input("home-top-row-container", "id"))
def update_top_row(_):
    df_pdrb = DATA["pdrb"]
    df_penduduk = DATA["penduduk"]

    # Calculate metrics
    prov_data = df_pdrb[(df_pdrb["kab_kota"] == PROVINSI_LABEL) & (df_pdrb["tahun"] == latest_year)]
    total_prov = prov_data["adhb"].sum() / 1000 if not prov_data.empty else 0 
    
    growth_df = hitung_laju_pertumbuhan(df_pdrb)
    growth_prov = growth_df[(growth_df["kab_kota"] == PROVINSI_LABEL) & (growth_df["tahun"] == latest_year)]
    growth_val = growth_prov["laju_pertumbuhan"].iloc[0] if not growth_prov.empty else 0

    perkapita_df = hitung_pdrb_perkapita(df_pdrb, df_penduduk)
    perkapita_prov = perkapita_df[(perkapita_df["kab_kota"] == PROVINSI_LABEL) & (perkapita_df["tahun"] == latest_year)]
    perkapita_val = perkapita_prov["pdrb_perkapita"].iloc[0] if not perkapita_prov.empty else 0

    return [
        html.Div(
            className="hero-card",
            children=[
                html.Div(
                    className="hero-text",
                    children=[
                        html.H2("Analisis PDRB Cepat, Hasil Presisi", className="hero-title"),
                        html.P("Wujudkan perencanaan ekonomi daerah yang tepat sasaran dengan layanan data yang komprehensif.", className="hero-subtitle"),
                        dcc.Link("Lihat Data Lengkap →", href="/monitoring", className="hero-button")
                    ]
                ),
                html.Img(src="/assets/maskot_1.webp", className="hero-mascot")
            ]
        ),
        html.Div(
            className="stat-cards-container",
            children=[
                html.Div(className="stat-card-custom", children=[
                    html.Img(src="/assets/maskot_2.webp", className="stat-card-mascot"),
                    html.Div(f"Total PDRB ({latest_year})", className="stat-label"),
                    html.Div(f"Rp {total_prov:,.0f} M", className="stat-value")
                ]),
                html.Div(className="stat-card-custom", children=[
                    html.Img(src="/assets/maskot_2.webp", className="stat-card-mascot"),
                    html.Div(f"PDRB Perkapita ({latest_year})", className="stat-label"),
                    html.Div(f"Rp {perkapita_val:,.1f} Jt", className="stat-value")
                ]),
                html.Div(className="stat-card-custom", children=[
                    html.Img(src="/assets/maskot_2.webp", className="stat-card-mascot"),
                    html.Div(f"Pertumbuhan ({latest_year})", className="stat-label"),
                    html.Div(f"{growth_val:.2f}%", className="stat-value")
                ])
            ]
        )
    ]


@callback(Output("home-main-chart", "figure"), Input("home-chart-tabs", "value"))
def update_main_chart(tipe_pdrb):
    df = DATA["pdrb"]
    sub = df[(df["kab_kota"] != PROVINSI_LABEL) & (df["tahun"] == latest_year)]
    sub = sub.groupby("kab_kota", as_index=False)[tipe_pdrb].sum()
    
    fig = px.bar(
        sub, x="kab_kota", y=tipe_pdrb,
        labels={tipe_pdrb: f"Total {tipe_pdrb.upper()}", "kab_kota": ""}
    )
    # Gunakan warna kuning/accent seperti di referensi
    fig.update_traces(marker_color=COLORS["accent"], width=0.4) 
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, linecolor="#EFEFEF"),
        yaxis=dict(showgrid=True, gridcolor="#EFEFEF", zeroline=False)
    )
    return fig


@callback(Output("home-list-container", "children"), Input("home-list-container", "id"))
def update_top_list(_):
    df = DATA["pdrb"]
    sub = df[(df["kab_kota"] != PROVINSI_LABEL) & (df["tahun"] == latest_year)]
    sub = sub.groupby("kab_kota", as_index=False)["adhb"].sum().sort_values("adhb", ascending=False).head(4)
    
    items = [html.H3("PDRB Tertinggi", className="list-title")]
    
    for i, row in sub.iterrows():
        items.append(
            html.Div(className="list-item", children=[
                html.Div(className="list-item-left", children=[
                    html.H4(row["kab_kota"]),
                    html.P(f"Tahun {latest_year}")
                ]),
                html.Div(f"Rp {row['adhb']/1000:,.0f} M", className="list-item-right")
            ])
        )
        
    items.append(dcc.Link("Selengkapnya →", href="/wilayah", className="selengkapnya-link"))
    return items
