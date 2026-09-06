from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, get_kab_kota_list, get_years_list
from utils.analysis import hitung_kontribusi, get_category_color_map
from utils.components import card

kab_kota_list = get_kab_kota_list()
years = get_years_list()

def layout():
    return html.Div([
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Kab/Kota", className="filter-label"),
                        dcc.Dropdown(id="kontribusi-kk", options=kab_kota_list, value=kab_kota_list[0], clearable=False),
                    ],
                ),
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Tahun", className="filter-label"),
                        dcc.Dropdown(id="kontribusi-tahun", options=years, value=max(years), clearable=False),
                    ],
                ),
            ],
        ),
        card("Kontribusi Lapangan Usaha terhadap PDRB", dcc.Graph(id="graf-kontribusi")),
    ])

@callback(Output("graf-kontribusi", "figure"), Input("kontribusi-kk", "value"), Input("kontribusi-tahun", "value"))
def update_kontribusi(kk, tahun):
    df_kontribusi = hitung_kontribusi(DATA["pdrb"], kk, tahun)
    color_map = get_category_color_map(df_kontribusi["lapangan_usaha"].tolist())
    fig = px.pie(
        df_kontribusi, names="lapangan_usaha", values="adhb", hole=0.45,
        color="lapangan_usaha", color_discrete_map=color_map,
    )
    fig.update_traces(textposition="inside", textinfo="percent")
    return fig
