from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from utils.data_loader import DATA, PROVINSI_LABEL, get_years_list
from utils.components import card
from theme import COLORS

years = get_years_list()

def layout():
    return html.Div([
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Tahun", className="filter-label"),
                        dcc.Dropdown(id="nominal-tahun", options=years, value=max(years), clearable=False),
                    ],
                )
            ],
        ),
        card("PDRB ADHB vs ADHK per Kab/Kota", dcc.Graph(id="graf-nominal")),
    ])

@callback(Output("graf-nominal", "figure"), Input("nominal-tahun", "value"))
def update_nominal(tahun):
    df = DATA["pdrb"]
    sub = df[(df["kab_kota"] != PROVINSI_LABEL) & (df["tahun"] == tahun)]
    sub = sub.groupby("kab_kota", as_index=False)[["adhb", "adhk"]].sum()
    fig = go.Figure()
    fig.add_bar(x=sub["kab_kota"], y=sub["adhb"], name="ADHB", marker_color=COLORS["primary"])
    fig.add_bar(x=sub["kab_kota"], y=sub["adhk"], name="ADHK", marker_color=COLORS["accent"])
    fig.update_layout(barmode="group", yaxis_title="Juta Rupiah")
    return fig
