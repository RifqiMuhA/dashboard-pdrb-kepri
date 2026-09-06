from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list
from utils.analysis import hitung_pdrb_perkapita, hitung_bonet
from utils.components import card
from theme import COLORS

years = get_years_list()

def layout():
    return html.Div([
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Tahun", className="filter-label"),
                        dcc.Dropdown(id="bonet-tahun", options=years, value=max(years), clearable=False),
                    ],
                )
            ],
        ),
        card("Indeks Bonet per Kab/Kota", dcc.Graph(id="graf-bonet")),
    ])

@callback(Output("graf-bonet", "figure"), Input("bonet-tahun", "value"))
def update_bonet(tahun):
    df_perkapita = hitung_pdrb_perkapita(DATA["pdrb"], DATA["penduduk"])
    df_bonet = hitung_bonet(df_perkapita, tahun, PROVINSI_LABEL).sort_values("indeks_bonet")
    fig = px.bar(df_bonet, x="indeks_bonet", y="kab_kota", orientation="h")
    fig.update_traces(marker_color=COLORS["primary"])
    fig.update_layout(xaxis_title="Indeks Bonet (deviasi terhadap provinsi)")
    return fig
