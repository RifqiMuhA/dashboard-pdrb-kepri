import dash
from dash import html, dcc, callback, Output, Input
from utils.components import page_heading

from tabs.wilayah import (
    tab_williamson,
    tab_bonet,
    tab_shiftshare,
    tab_lq,
    tab_klassen,
)

dash.register_page(__name__, path="/wilayah", name="Analisis Antar Wilayah")

layout = html.Div(
    [
        page_heading("Analisis Antar Wilayah", "Indeks Williamson, Indeks Bonet, Shift Share, LQ, dan Tipologi Klassen"),
        dcc.Tabs(
            id="wilayah-tabs",
            className="custom-tabs",
            value="williamson",
            children=[
                dcc.Tab(label="Indeks Williamson", value="williamson", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Indeks Bonet", value="bonet", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Shift Share", value="shiftshare", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="LQ", value="lq", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Tipologi Klassen", value="klassen", className="tab", selected_className="tab--selected"),
            ],
        ),
        html.Div(id="wilayah-content", style={"marginTop": "20px"}),
    ]
)

@callback(Output("wilayah-content", "children"), Input("wilayah-tabs", "value"))
def render_tab(tab):
    if tab == "williamson":
        return tab_williamson.layout()
    elif tab == "bonet":
        return tab_bonet.layout()
    elif tab == "shiftshare":
        return tab_shiftshare.layout()
    elif tab == "lq":
        return tab_lq.layout()
    elif tab == "klassen":
        return tab_klassen.layout()
    return html.Div()
