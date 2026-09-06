from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_tax_ratio
from utils.components import card
from theme import COLORS

def layout():
    return card("Tax Ratio", dcc.Graph(id="graf-tax"))

@callback(Output("graf-tax", "figure"), Input("makro-tabs", "value"))
def update_tax(_):
    df = hitung_tax_ratio(DATA["pajak_provinsi"], DATA["pdrb"], PROVINSI_LABEL)
    fig = px.line(df, x="tahun", y="tax_ratio", markers=True)
    fig.update_traces(line_color=COLORS["primary"])
    fig.update_layout(yaxis_title="Tax Ratio (%)")
    return fig
