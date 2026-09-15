import dash
from dash import html, dcc, callback, Output, Input
from utils.data_loader import PROVINSI_LABEL
from utils.components import page_heading

from tabs.makro import (
    tab_konsumsi,
    tab_rpi,
    tab_icor,
    tab_ilor,
    tab_tax,
)

dash.register_page(__name__, path="/makro", name="Analisis Makro Ekonomi")

layout = html.Div(
    [
        page_heading("Analisis Makro Ekonomi", f"Level {PROVINSI_LABEL} — komponen pengeluaran umumnya tidak tersedia per kab/kota"),
        dcc.Tabs(
            id="makro-tabs",
            className="custom-tabs",
            value="konsumsi",
            children=[
                dcc.Tab(label="Konsumsi RT (APC & MPC)", value="konsumsi", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="RPI", value="rpi", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="ICOR", value="icor", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="ILOR & Elastisitas TK", value="ilor", className="tab", selected_className="tab--selected"),
                dcc.Tab(label="Tax Ratio", value="tax", className="tab", selected_className="tab--selected"),
            ],
        ),
        html.Div(id="makro-content", style={"marginTop": "20px"}),
    ]
)

@callback(Output("makro-content", "children"), Input("makro-tabs", "value"))
def render_tab(tab):
    if tab == "konsumsi":
        return tab_konsumsi.layout()
    elif tab == "rpi":
        return tab_rpi.layout()
    elif tab == "icor":
        return tab_icor.layout()
    elif tab == "ilor":
        return tab_ilor.layout()
    elif tab == "tax":
        return tab_tax.layout()
    return html.Div()
