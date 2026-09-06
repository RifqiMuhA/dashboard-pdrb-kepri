import dash
from dash import Dash, html, dcc, Input, Output

from theme import register_template
from utils.components import build_header, build_sidebar

register_template()  # daftarkan Plotly template custom sebagai default

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    title="Dashboard Analisis PDB/PDRB",
)
server = app.server  # untuk deployment (gunicorn, dsb.)

app.layout = html.Div(
    className="app-container",
    children=[
        dcc.Location(id="url"),
        html.Div(id="sidebar-container"),
        html.Div(
            className="main-panel",
            children=[
                build_header(),
                html.Div(className="content-area", children=dash.page_container),
            ],
        ),
    ]
)


@app.callback(Output("sidebar-container", "children"), Input("url", "pathname"))
def update_sidebar(pathname):
    return build_sidebar(pathname)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
