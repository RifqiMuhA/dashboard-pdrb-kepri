from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_kab_kota_list
from utils.analysis import hitung_indeks_implisit
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
                        dcc.Dropdown(id="implisit-kk", options=[PROVINSI_LABEL] + kab_kota_list, value=PROVINSI_LABEL, clearable=False),
                    ],
                )
            ],
        ),
        card("Indeks Implisit & Laju Indeks Implisit", dcc.Graph(id="graf-implisit")),
    ])

@callback(Output("graf-implisit", "figure"), Input("implisit-kk", "value"))
def update_implisit(kk):
    df_impl = hitung_indeks_implisit(DATA["pdrb"], kk)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_impl["tahun"], y=df_impl["indeks_implisit"], mode="lines+markers", name="Indeks Implisit", line=dict(color=COLORS["primary"])))
    fig.add_trace(go.Scatter(x=df_impl["tahun"], y=df_impl["laju_indeks_implisit"], mode="lines+markers", name="Laju Indeks Implisit (%)", line=dict(color=COLORS["accent"]), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Indeks Implisit"),
        yaxis2=dict(title="Laju (%)", overlaying="y", side="right"),
    )
    return fig
