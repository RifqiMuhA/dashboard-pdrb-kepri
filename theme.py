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
    "#2A9D8F",
    "#E76F51",
    "#7209B7",
    "#4361EE",
    "#4CC9F0",
    "#52B788",
    "#8D99AE",
    "#EF476F",
    "#B56576",
]

# Mapping warna konsisten per Kabupaten/Kota di Kepulauan Riau
KABKOTA_COLORS = {
    "Kabupaten Karimun": "#1B5FAE",
    "Kabupaten Bintan": "#F2B705",        # Kuning aksen (sorotan analisis)
    "Kabupaten Natuna": "#2A9D8F",        # Teal / Hijau Laut
    "Kabupaten Lingga": "#E76F51",        # Coral / Terracotta
    "Kabupaten Kepulauan Anambas": "#457B9D", # Slate Blue
    "Kota Batam": "#0C203A",              # Navy Gelap (kontras industri)
    "Kota Tanjungpinang": "#7209B7",      # Violet / Ungu Elegan
    "Provinsi Kepulauan Riau": "#C99204", # Kuning Tua / Garis Referensi
}

# Mapping warna konsisten per Lapangan Usaha (17 Sektor Utama)
SEKTOR_COLORS = {
    "A": "#2A9D8F",  # Pertanian, Kehutanan dan Perikanan
    "B": "#70798C",  # Pertambangan dan Penggalian
    "C": "#173A66",  # Industri Pengolahan (Primary Navy)
    "D": "#F4A261",  # Pengadaan Listrik dan Gas
    "E": "#52B788",  # Pengadaan Air, Pengelolaan Sampah
    "F": "#E76F51",  # Konstruksi
    "G": "#34659D",  # Perdagangan Besar dan Eceran
    "H": "#457B9D",  # Transportasi dan Pergudangan
    "I": "#F2B705",  # Penyediaan Akomodasi dan Makan Minum (Pariwisata)
    "J": "#7209B7",  # Informasi dan Komunikasi
    "K": "#3A0CA3",  # Jasa Keuangan dan Asuransi
    "L": "#4361EE",  # Real Estat
    "M,N": "#4CC9F0", # Jasa Perusahaan
    "O": "#8D99AE",  # Administrasi Pemerintahan
    "P": "#06D6A0",  # Jasa Pendidikan
    "Q": "#EF476F",  # Jasa Kesehatan
    "R,S,T,U": "#B56576", # Jasa Lainnya
}

def get_sektor_color_by_name(nama_lu: str) -> str:
    """Mengambil warna sektor berdasarkan kode awal nama lapangan usaha."""
    for kode, color in SEKTOR_COLORS.items():
        if nama_lu.startswith(f"{kode}."):
            return color
    return COLORS["primary"]

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
