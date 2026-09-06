from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list
from utils.analysis import hitung_lq_matrix
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
                        dcc.Dropdown(id="lq-tahun", options=years, value=max(years), clearable=False),
                    ],
                )
            ],
        ),
        card("Heatmap LQ (Lapangan Usaha x Kab/Kota)", dcc.Graph(id="graf-lq")),
    ])

@callback(Output("graf-lq", "figure"), Input("lq-tahun", "value"))
def update_lq(tahun):
    df_lq = hitung_lq_matrix(DATA["pdrb"], PROVINSI_LABEL, tahun)
    pivot = df_lq.pivot(index="lapangan_usaha", columns="kab_kota", values="lq")
    fig = px.imshow(
        pivot, text_auto=".2f", aspect="auto",
        color_continuous_scale=[[0, COLORS["gray_light"]], [0.5, COLORS["primary_light"]], [1, COLORS["primary_dark"]]],
        labels=dict(color="LQ"),
    )
    return fig
