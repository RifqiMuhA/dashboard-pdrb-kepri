from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_icor
from utils.components import card
from theme import COLORS

def layout():
    return card("Incremental Capital Output Ratio (ICOR)", dcc.Graph(id="graf-icor"))

@callback(Output("graf-icor", "figure"), Input("makro-tabs", "value"))
def update_icor(_):
    df = hitung_icor(DATA["pdrb"], DATA["pengeluaran_provinsi"], PROVINSI_LABEL)
    fig = px.bar(df, x="tahun", y="icor")
    fig.update_traces(marker_color=COLORS["primary"])
    return fig
