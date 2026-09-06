from dash import html, dcc
from dash_iconify import DashIconify

MENU_ITEMS = [
    {"label": "Beranda", "path": "/", "icon": "lucide:home"},
    {"label": "Monitoring Perilaku Ekonomi", "path": "/monitoring", "icon": "lucide:bar-chart-2"},
    {"label": "Analisis Antar Wilayah", "path": "/wilayah", "icon": "lucide:map"},
    {"label": "Analisis Makro Ekonomi", "path": "/makro", "icon": "lucide:trending-up"},
    {"label": "Data Explorer", "path": "/explorer", "icon": "lucide:table"},
]


def build_header(title: str = "Dashboard Analisis PDB/PDRB"):
    return html.Div(
        className="app-header",
        children=[
            html.H1(title),
        ],
    )


def build_sidebar(current_path: str = "/"):
    links = []
    
    # Bagian Logo
    logo = html.Div(
        className="sidebar-logo-container",
        children=[
            DashIconify(icon="lucide:pie-chart", width=28, className="logo-icon"),
            html.Span("PDRB Dash", className="logo-text")
        ]
    )
    
    menu_label = html.Div("MENU", className="sidebar-menu-label")
    
    for item in MENU_ITEMS:
        is_active = current_path == item["path"]
        links.append(
            dcc.Link(
                children=[
                    DashIconify(icon=item["icon"], width=20, className="sidebar-icon"),
                    html.Span(item["label"])
                ],
                href=item["path"],
                className="sidebar-link" + (" active" if is_active else ""),
            )
        )
        
    nav_links = html.Div(className="sidebar-nav", children=[menu_label] + links)
    return html.Div(className="sidebar", children=[logo, nav_links])


def kpi_card(label: str, value: str):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(value, className="kpi-value"),
            html.Div(label, className="kpi-label"),
        ],
    )


def card(title: str, children):
    content = [html.Div(title, className="card-title")] if title else []
    content.append(children)
    return html.Div(className="card-box", children=content)


def page_heading(title: str, subtitle: str = ""):
    els = [html.Div(title, className="page-title")]
    if subtitle:
        els.append(html.Div(subtitle, className="page-subtitle"))
    return html.Div(els)
