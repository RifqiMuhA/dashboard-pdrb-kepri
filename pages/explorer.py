import dash
from dash import html, dcc, dash_table, callback, Output, Input

from utils.data_loader import DATA
from utils.components import card, page_heading
from theme import COLORS

dash.register_page(__name__, path="/explorer", name="Data Explorer")

DATASET_OPTIONS = [
    {"label": "PDRB (ADHB & ADHK)", "value": "pdrb"},
    {"label": "Penduduk", "value": "penduduk"},
    {"label": "Pengeluaran (Provinsi)", "value": "pengeluaran_provinsi"},
    {"label": "Pajak (Provinsi)", "value": "pajak_provinsi"},
    {"label": "Tenaga Kerja (Provinsi)", "value": "tenaga_kerja_provinsi"},
]

layout = html.Div(
    [
        page_heading("Data Explorer", "Lihat data mentah yang dipakai di seluruh dashboard"),
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-item",
                    children=[
                        html.Label("Pilih Dataset", className="filter-label"),
                        dcc.Dropdown(id="explorer-dataset", options=DATASET_OPTIONS, value="pdrb", clearable=False),
                    ],
                )
            ],
        ),
        card(None, html.Div(id="explorer-table")),
    ]
)


@callback(Output("explorer-table", "children"), Input("explorer-dataset", "value"))
def update_table(dataset_key):
    df = DATA[dataset_key]
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "Inter, sans-serif", "fontSize": "13px", "padding": "6px 10px"},
        style_header={"backgroundColor": COLORS["primary"], "color": "white", "fontWeight": "600"},
        style_data={"backgroundColor": "white"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": COLORS["gray_light"]}
        ],
    )
