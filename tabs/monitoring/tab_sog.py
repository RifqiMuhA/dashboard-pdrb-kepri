from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, get_kab_kota_list
from utils.analysis import hitung_sumber_pertumbuhan, get_category_color_map
from utils.components import card

kab_kota_list = get_kab_kota_list()

def layout():
    return html.Div([
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Kab/Kota", className="filter-label"),
                        dcc.Dropdown(id="sog-kk", options=kab_kota_list, value=kab_kota_list[0], clearable=False),
                    ],
                )
            ],
        ),
        card("Sumber Pertumbuhan (SOG) per Lapangan Usaha", dcc.Graph(id="graf-sog")),
    ])

@callback(Output("graf-sog", "figure"), Input("sog-kk", "value"))
def update_sog(kk):
    df_sog = hitung_sumber_pertumbuhan(DATA["pdrb"], kk)
    color_map = get_category_color_map(df_sog["lapangan_usaha"].unique().tolist())
    fig = px.bar(
        df_sog, x="tahun", y="sog", color="lapangan_usaha", color_discrete_map=color_map,
        labels={"sog": "Sumber Pertumbuhan (%)"},
    )
    fig.update_layout(barmode="relative")
    return fig
