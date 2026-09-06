from dash import html, dcc, callback, Output, Input
import plotly.express as px
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_tipologi_klassen, get_category_color_map
from utils.components import card
from theme import REFERENCE_LINE_STYLE

def layout():
    return card("Tipologi Klassen (rata-rata seluruh periode data)", dcc.Graph(id="graf-klassen"))

@callback(Output("graf-klassen", "figure"), Input("wilayah-tabs", "value"))
def update_klassen(_):
    years_avail = sorted(DATA["pdrb"]["tahun"].unique())
    df_klassen = hitung_tipologi_klassen(DATA["pdrb"], DATA["penduduk"], PROVINSI_LABEL, years_avail[0], years_avail[-1])
    color_map = get_category_color_map(df_klassen["kuadran"].unique().tolist())
    fig = px.scatter(
        df_klassen, x="pdrb_perkapita", y="laju_pertumbuhan", color="kuadran", text="kab_kota",
        color_discrete_map=color_map,
    )
    fig.update_traces(textposition="top center", marker=dict(size=12))
    ref_perkapita = df_klassen.attrs.get("ref_perkapita")
    ref_growth = df_klassen.attrs.get("ref_growth")
    if ref_perkapita is not None:
        fig.add_vline(x=ref_perkapita, line=REFERENCE_LINE_STYLE)
    if ref_growth is not None:
        fig.add_hline(y=ref_growth, line=REFERENCE_LINE_STYLE)
    fig.update_layout(xaxis_title="Rata-rata PDRB Perkapita", yaxis_title="Rata-rata Laju Pertumbuhan (%)")
    return fig
