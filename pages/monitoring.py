import dash
from dash import html, dcc, callback, Output, Input
from utils.components import page_heading

from tabs.monitoring import (
    tab_nominal,
    tab_pertumbuhan,
    tab_kontribusi,
    tab_perkapita,
    tab_sog,
    tab_implisit,
)

dash.register_page(__name__, path="/monitoring", name="Monitoring Perilaku Ekonomi")

layout = html.Div(
    [
        page_heading("Monitoring Perilaku Ekonomi", "Nilai nominal, pertumbuhan, kontribusi, dan indikator turunan PDRB"),
        dcc.Tabs(
            id="monitoring-tabs",
            className="custom-tabs",
            value="nominal",
            children=[
                dcc.Tab(label="Nilai Nominal", value="nominal", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Laju Pertumbuhan", value="pertumbuhan", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Kontribusi", value="kontribusi", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="PDRB Perkapita", value="perkapita", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Sumber Pertumbuhan", value="sog", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Indeks Implisit", value="implisit", className="tab", selected_className="tab--selected"),
            ],
        ),
        html.Div(id="monitoring-content", style={"marginTop": "20px"}),
    ]
)

@callback(Output("monitoring-content", "children"), Input("monitoring-tabs", "value"))
def render_tab(tab):
    if tab == "nominal":
        return tab_nominal.layout()
    elif tab == "pertumbuhan":
        return tab_pertumbuhan.layout()
    elif tab == "kontribusi":
        return tab_kontribusi.layout()
    elif tab == "perkapita":
        return tab_perkapita.layout()
    elif tab == "sog":
        return tab_sog.layout()
    elif tab == "implisit":
        return tab_implisit.layout()
    return html.Div()
