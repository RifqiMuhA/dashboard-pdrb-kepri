from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_pdrb_perkapita
from utils.components import card
from theme import COLORS, REFERENCE_LINE_STYLE

def layout():
    return card("PDRB Perkapita per Kab/Kota (Tahun Terbaru)", dcc.Graph(id="graf-perkapita"))

@callback(Output("graf-perkapita", "figure"), Input("monitoring-tabs", "value"))
def update_perkapita(_):
    df_perkapita = hitung_pdrb_perkapita(DATA["pdrb"], DATA["penduduk"])
    latest = df_perkapita["tahun"].max()
    sub = df_perkapita[(df_perkapita["kab_kota"] != PROVINSI_LABEL) & (df_perkapita["tahun"] == latest)].sort_values("pdrb_perkapita")
    ref_val = df_perkapita[(df_perkapita["kab_kota"] == PROVINSI_LABEL) & (df_perkapita["tahun"] == latest)]["pdrb_perkapita"]
    fig = px.bar(sub, x="kab_kota", y="pdrb_perkapita", labels={"pdrb_perkapita": "PDRB Perkapita (juta Rp/jiwa)"})
    fig.update_traces(marker_color=COLORS["primary"])
    if not ref_val.empty:
        fig.add_hline(y=ref_val.iloc[0], line=REFERENCE_LINE_STYLE, annotation_text=f"Rata-rata {PROVINSI_LABEL}")
    return fig
