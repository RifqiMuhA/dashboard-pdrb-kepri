from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_pdrb_perkapita, hitung_williamson_series
from utils.components import card
from theme import COLORS

def layout():
    return card("Tren Indeks Williamson", dcc.Graph(id="graf-williamson"))

@callback(Output("graf-williamson", "figure"), Input("wilayah-tabs", "value"))
def update_williamson(_):
    df_perkapita = hitung_pdrb_perkapita(DATA["pdrb"], DATA["penduduk"])
    df_perkapita_kk = df_perkapita[df_perkapita["kab_kota"] != PROVINSI_LABEL]
    df_penduduk_kk = DATA["penduduk"][DATA["penduduk"]["kab_kota"] != PROVINSI_LABEL]
    result = hitung_williamson_series(df_perkapita_kk, df_penduduk_kk)
    fig = px.line(result, x="tahun", y="indeks_williamson", markers=True)
    fig.update_traces(line_color=COLORS["primary"])
    fig.update_layout(yaxis_title="Indeks Williamson (0-1)", yaxis_range=[0, 1])
    return fig
