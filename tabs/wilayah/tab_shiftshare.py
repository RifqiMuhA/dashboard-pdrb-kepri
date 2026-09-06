from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_kab_kota_list
from utils.analysis import hitung_shift_share
from utils.components import card
from theme import COLORS

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
                        dcc.Dropdown(id="ss-kk", options=kab_kota_list, value=kab_kota_list[0], clearable=False),
                    ],
                )
            ],
        ),
        card("Komponen Shift Share per Lapangan Usaha", dcc.Graph(id="graf-shiftshare")),
    ])

@callback(Output("graf-shiftshare", "figure"), Input("ss-kk", "value"))
def update_shiftshare(kk):
    years_avail = sorted(DATA["pdrb"]["tahun"].unique())
    df_ss = hitung_shift_share(DATA["pdrb"], kk, PROVINSI_LABEL, years_avail[0], years_avail[-1])
    fig = go.Figure()
    fig.add_bar(x=df_ss["lapangan_usaha"], y=df_ss["regional_share"], name="Regional Share", marker_color=COLORS["primary"])
    fig.add_bar(x=df_ss["lapangan_usaha"], y=df_ss["proportional_shift"], name="Proportional Shift", marker_color=COLORS["accent"])
    fig.add_bar(x=df_ss["lapangan_usaha"], y=df_ss["differential_shift"], name="Differential Shift", marker_color=COLORS["primary_light"])
    fig.update_layout(barmode="relative", yaxis_title="Nilai Shift Share")
    return fig
