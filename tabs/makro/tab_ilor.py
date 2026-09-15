from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_ilor_elastisitas
from utils.components import card
from theme import COLORS

def layout():
    return card("ILOR & Elastisitas Tenaga Kerja per Lapangan Usaha", dcc.Graph(id="graf-ilor"))

@callback(Output("graf-ilor", "figure"), Input("makro-tabs", "value"))
def update_ilor(_):
    df = hitung_ilor_elastisitas(DATA["tenaga_kerja_provinsi"], DATA["pdrb"], PROVINSI_LABEL)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Data tenaga kerja provinsi belum tersedia"),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig
    fig = go.Figure()
    fig.add_bar(x=df["lapangan_usaha"], y=df["ilor"], name="ILOR", marker_color=COLORS["primary"])
    fig.add_bar(x=df["lapangan_usaha"], y=df["elastisitas_tk"], name="Elastisitas TK", marker_color=COLORS["accent"])
    fig.update_layout(barmode="group")
    return fig
