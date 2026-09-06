from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA
from utils.analysis import hitung_apc_aps
from utils.components import card
from theme import COLORS

def layout():
    return card("APC (Average Propensity to Consume) & APS (Average Propensity to Save)", dcc.Graph(id="graf-apc"))

@callback(Output("graf-apc", "figure"), Input("makro-tabs", "value"))
def update_apc(_):
    df = hitung_apc_aps(DATA["pengeluaran_provinsi"])
    fig = go.Figure()
    fig.add_bar(x=df["tahun"], y=df["apc"], name="APC", marker_color=COLORS["primary"])
    fig.add_bar(x=df["tahun"], y=df["aps"], name="APS", marker_color=COLORS["accent"])
    fig.update_layout(barmode="stack", yaxis_title="Proporsi")
    return fig
