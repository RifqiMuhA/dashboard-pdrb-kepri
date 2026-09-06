from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA
from utils.analysis import hitung_rpi
from utils.components import card
from theme import COLORS

def layout():
    return card("Rasio Perdagangan Internasional (RPI)", dcc.Graph(id="graf-rpi"))

@callback(Output("graf-rpi", "figure"), Input("makro-tabs", "value"))
def update_rpi(_):
    df = hitung_rpi(DATA["pengeluaran_provinsi"])
    fig = px.line(df, x="tahun", y="rpi", markers=True)
    fig.update_traces(line_color=COLORS["primary"])
    fig.add_hline(y=0, line_dash="dot", line_color=COLORS["gray_mid"])
    fig.update_layout(yaxis_title="RPI (-1 s/d 1)", yaxis_range=[-1, 1])
    return fig
