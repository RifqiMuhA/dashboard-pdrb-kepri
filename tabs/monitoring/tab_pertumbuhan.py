from dash import html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL
from utils.analysis import hitung_laju_pertumbuhan
from utils.components import card
from theme import REFERENCE_LINE_STYLE

def layout():
    return card("Laju Pertumbuhan Ekonomi per Kab/Kota (dengan garis referensi provinsi)", dcc.Graph(id="graf-pertumbuhan"))

@callback(Output("graf-pertumbuhan", "figure"), Input("monitoring-tabs", "value"))
def update_pertumbuhan(_):
    growth_df = hitung_laju_pertumbuhan(DATA["pdrb"])
    prov_growth = growth_df[growth_df["kab_kota"] == PROVINSI_LABEL].dropna(subset=["laju_pertumbuhan"])
    kk_growth = growth_df[growth_df["kab_kota"] != PROVINSI_LABEL].dropna(subset=["laju_pertumbuhan"])

    fig = px.line(kk_growth, x="tahun", y="laju_pertumbuhan", color="kab_kota", markers=True)
    if not prov_growth.empty:
        fig.add_trace(
            go.Scatter(
                x=prov_growth["tahun"], y=prov_growth["laju_pertumbuhan"],
                mode="lines", name=f"Rata-rata {PROVINSI_LABEL}", line=REFERENCE_LINE_STYLE,
            )
        )
    fig.update_layout(yaxis_title="Laju Pertumbuhan (%)", xaxis_title="Tahun")
    return fig
