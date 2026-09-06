"""
Definisi warna, tipografi, dan Plotly template untuk Dashboard PDRB.
Ubah nilai di sini untuk mengubah tampilan di seluruh aplikasi.
"""

import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# 1. PALET WARNA
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#173A66",        # Biru Tua Profesional
    "primary_dark": "#0C203A",   # Biru Sangat Gelap
    "primary_light": "#34659D",  # Biru Menengah
    "accent": "#F2B705",         # Kuning
    "accent_dark": "#C99204",    # Kuning Tua
    "gray_dark": "#4A4A4A",      # Abu Tua (teks)
    "gray_mid": "#9B9B9B",       # Abu Sedang (grid, teks sekunder)
    "gray_light": "#EFEFEF",     # Abu Muda (background)
    "white": "#FFFFFF",
}

# Palet kategori untuk chart dengan banyak seri (mis. lapangan usaha).
# Urutan tetap dipakai konsisten di semua chart lewat mapping warna kategori
# (lihat utils/analysis.py -> get_category_color_map).
CATEGORY_PALETTE = [
    COLORS["primary"],
    COLORS["accent"],
    COLORS["primary_light"],
    COLORS["accent_dark"],
    COLORS["gray_mid"],
    COLORS["primary_dark"],
    "#7FB3E8",
    "#F7D269",
]

FONT_FAMILY = "Inter, -apple-system, Segoe UI, sans-serif"

# ---------------------------------------------------------------------------
# 2. PLOTLY TEMPLATE CUSTOM
# ---------------------------------------------------------------------------
def build_plotly_template() -> go.layout.Template:
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family=FONT_FAMILY, size=12, color=COLORS["gray_dark"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORY_PALETTE,
        title=dict(font=dict(size=16, color=COLORS["primary_dark"])),
        xaxis=dict(
            gridcolor=COLORS["gray_light"],
            linecolor=COLORS["gray_mid"],
            zerolinecolor=COLORS["gray_mid"],
        ),
        yaxis=dict(
            gridcolor=COLORS["gray_light"],
            linecolor=COLORS["gray_mid"],
            zerolinecolor=COLORS["gray_mid"],
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=COLORS["gray_dark"]),
        ),
        margin=dict(l=50, r=30, t=50, b=40),
    )
    return template


def register_template():
    """Panggil sekali di app.py agar semua chart otomatis pakai tema ini."""
    pio.templates["pdrb_theme"] = build_plotly_template()
    pio.templates.default = "pdrb_theme"


# Style referensi (garis rata-rata nasional/provinsi, batas kuadran, dsb.)
REFERENCE_LINE_STYLE = dict(color=COLORS["accent_dark"], dash="dash", width=2)
