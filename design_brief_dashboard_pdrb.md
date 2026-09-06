# Design Brief — Dashboard Analisis PDB/PDRB (Plotly Dash)

## 1. Tujuan
Dashboard interaktif untuk memonitor dan menganalisis PDRB suatu wilayah (provinsi & kabupaten/kota), mengikuti tiga kerangka analisis: Monitoring Perilaku Ekonomi, Analisis Antar Wilayah, dan Analisis Makro Ekonomi.

## 2. Palet Warna

| Peran | Nama | Hex | Kegunaan |
|---|---|---|---|
| Primary | Biru Kuat (Strong Blue) | `#1B5FAE` | Sidebar, header, elemen chart utama, tombol aktif |
| Primary — Dark | Biru Gelap | `#123E73` | Teks di atas latar terang, hover state elemen biru |
| Primary — Light | Biru Muda | `#5A93D1` | Aksen sekunder, area chart transparan |
| Accent | Kuning | `#F2B705` | Highlight, garis referensi pada chart, penanda nilai penting |
| Accent — Dark | Kuning Tua | `#C99204` | Teks/border di atas latar terang bila kontras kuning terang kurang cukup |
| Netral — Gelap | Abu Tua | `#4A4A4A` | Teks judul, label sumbu |
| Netral — Sedang | Abu Sedang | `#9B9B9B` | Teks sekunder, garis grid |
| Netral — Terang | Abu Muda | `#EFEFEF` | Background halaman, divider |
| Base | Putih | `#FFFFFF` | Background card/konten |

**Komposisi:** Biru ±55%, Abu ±35%, Kuning ±10% (aksen saja, jangan jadi warna area luas).

**Aturan kontras:**
- Kuning tidak dipakai untuk teks di atas putih (kontras rendah) — kuning hanya untuk background aksen kecil, border, garis chart, atau ikon.
- Teks putih hanya di atas Biru Kuat / Biru Gelap.
- Teks utama pada background putih/abu muda memakai Abu Tua, bukan hitam pekat.

## 3. Tipografi
- Font: **Inter** atau **Nunito Sans** (Google Fonts, muat via `assets/`).
- Judul halaman: 22–26px, semi-bold, warna Biru Gelap.
- Judul chart/card: 15–16px, semi-bold, Abu Tua.
- Body/label/angka tabel: 13px, regular, Abu Tua.
- Angka KPI besar: 28–32px, bold, Biru Kuat.

## 4. Layout

```
┌───────────────────────────────────────────────┐
│  HEADER (judul dashboard)                      │
├───────────┬─────────────────────────────────────┤
│           │                                     │
│  SIDEBAR  │           KONTEN UTAMA              │
│  (5 menu) │   (card putih di atas Abu Muda)     │
│           │                                     │
└───────────┴─────────────────────────────────────┘
```

- Sidebar: background Biru Kuat, teks putih. Menu aktif ditandai garis vertikal Kuning di sisi kiri item (bukan background penuh kuning).
- Konten: card putih, `border-radius: 8px`, `box-shadow` tipis, jarak antar card konsisten (16–24px).
- Header: background putih atau Abu Muda, border-bottom tipis Abu Sedang.

## 5. Struktur Menu

1. **Beranda** — ringkasan KPI, highlight tertinggi/terendah antar kab/kota.
2. **Monitoring Perilaku Ekonomi** — sub-tab: Nilai Nominal, Laju Pertumbuhan, Kontribusi/Peranan, PDRB Perkapita, Sumber Pertumbuhan, Indeks & Laju Implisit.
3. **Analisis Antar Wilayah** — sub-tab: Indeks Williamson, Indeks Bonet, Shift Share, LQ, Tipologi Klassen.
4. **Analisis Makro Ekonomi** — sub-tab: Konsumsi RT (MPC/APC), RPI, ICOR, ILOR & Elastisitas Tenaga Kerja, Tax Ratio.
5. **Data Explorer** — tabel data mentah & olahan, filter, unduh CSV/Excel.

Navigasi antar sub-tab dalam satu menu memakai tab horizontal, bukan dropdown, supaya konteks kelompok analisis tetap terlihat.

## 6. Styling Komponen

- **KPI Card:** background putih, angka besar Biru Kuat, label kecil Abu Sedang, garis aksen tipis Kuning di tepi atas card.
- **Chart (Plotly template custom):**
  - Background plot & paper: putih/transparan.
  - Warna seri data utama: Biru Kuat, Biru Muda untuk seri kedua.
  - Garis referensi (rata-rata nasional/provinsi, batas kuadran, dsb.): Kuning, dashed.
  - Grid: Abu Muda tipis.
  - Font chart: sama dengan font dashboard, ukuran 12px.
- **Tabel (dash_table):** header Biru Kuat teks putih, baris zebra putih/Abu Muda, border Abu Sedang tipis, sorting aktif ditandai indikator Biru.
- **Dropdown/Input filter:** border Abu Sedang, border jadi Biru saat fokus, tombol submit/apply berwarna Biru Kuat teks putih.
- **Tab:** tab aktif — underline tebal Kuning, teks Biru Gelap bold; tab non-aktif — teks Abu Sedang.

## 7. Ikon
Gunakan icon library berbasis SVG line-icon (misalnya Lucide/Feather via `dash-iconify` atau file SVG custom) untuk tiap menu sidebar dan KPI card. Hindari emoji sebagai pengganti ikon — gaya visual harus konsisten satu set garis (stroke width & style seragam), bukan campuran karakter emoji.

## 8. Konsistensi Warna Kategori
Jika ada kategori berulang di banyak chart (misalnya 17 lapangan usaha, atau daftar kab/kota), tetapkan satu mapping warna tetap di awal (misal lewat dictionary Python) dan pakai di semua chart — jangan biarkan Plotly assign warna otomatis yang bisa berubah urutan antar chart.

## 9. Referensi Teknis Implementasi (untuk tahap coding nanti)
- Simpan definisi warna & font di satu file konstanta (`theme.py` atau `assets/style.css` + variabel CSS custom properties) agar mudah diubah sekali dan konsisten di seluruh aplikasi.
- Buat Plotly template custom (`plotly.io.templates["pdrb_theme"]`) yang mereferensikan palet ini, di-set sebagai default template di awal aplikasi.
