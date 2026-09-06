# Dashboard Analisis PDB/PDRB (Plotly Dash)

Dashboard interaktif untuk analisis PDRB: Monitoring Perilaku Ekonomi, Analisis
Antar Wilayah, dan Analisis Makro Ekonomi — mengikuti kerangka pada materi
"Analisis PDB/PDRB".

## Struktur Folder

```
pdrb_dashboard/
├── app.py                  # entry point, jalankan ini
├── theme.py                 # warna & Plotly template custom
├── requirements.txt
├── assets/
│   └── style.css            # styling layout (auto-terdeteksi oleh Dash)
├── data/
│   ├── generate_sample_data.py  # generator data CONTOH (sintetis)
│   └── sample_data.xlsx         # data yang dipakai aplikasi (ganti dengan data asli)
├── utils/
│   ├── data_loader.py        # load Excel -> dict of DataFrame
│   ├── analysis.py           # semua rumus (laju pertumbuhan, Williamson, LQ, dst.)
│   └── components.py         # komponen UI reusable (header, sidebar, KPI card)
└── pages/
    ├── beranda.py
    ├── monitoring.py
    ├── wilayah.py
    ├── makro.py
    └── explorer.py
```

## Cara Menjalankan

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Buka `http://localhost:8050` di browser.

## Cara Mengganti dengan Data Asli

1. Siapkan data kalian dalam format **long/tidy** (satu baris = satu observasi),
   BUKAN format tabel lebar ala publikasi BPS. Skema tiap sheet ada di docstring
   `utils/data_loader.py`:

   | Sheet | Kolom wajib |
   |---|---|
   | `pdrb` | kab_kota, lapangan_usaha, tahun, adhb, adhk |
   | `penduduk` | kab_kota, tahun, jumlah_penduduk |
   | `pengeluaran_provinsi` | tahun, uraian, adhb, adhk |
   | `pajak_provinsi` | tahun, penerimaan_pajak, penerimaan_sda |
   | `tenaga_kerja_provinsi` | tahun, lapangan_usaha, jumlah_tenaga_kerja |

   Sheet `pdrb` dan `penduduk` **harus** menyertakan satu baris/level untuk
   "Provinsi" (agregat total) sebagai wilayah acuan — dipakai sebagai
   pembanding di banyak analisis (Williamson, Bonet, Shift Share, LQ, Klassen).

2. Timpa file `data/sample_data.xlsx` dengan data asli kalian (nama sheet & 
   kolom harus sama persis), atau ubah `DATA_PATH` di `utils/data_loader.py`
   kalau nama filenya beda.

3. Sesuaikan `PROVINSI_LABEL` di `utils/data_loader.py` dengan label wilayah
   acuan kalian (misalnya nama provinsi asli).

4. Jalankan ulang `python app.py` — tidak perlu ubah kode di `pages/` sama sekali,
   selama skema data konsisten.

## Catatan Penting

- **Data pengeluaran, pajak, dan tenaga kerja** di skeleton ini disiapkan
  hanya di **level provinsi**, karena BPS umumnya tidak menerbitkan PDRB
  menurut pengeluaran atau data ketenagakerjaan sampai level kab/kota. Kalau
  provinsi kalian ternyata punya data ini per kab/kota, sheet-nya bisa
  ditambah kolom `kab_kota` dan fungsi di `utils/analysis.py` (hitung_apc_aps,
  hitung_icor, dst.) disesuaikan untuk menerima parameter wilayah.
- Semua warna & styling terpusat di `theme.py` + `assets/style.css` — ubah
  di situ untuk mengubah tampilan seluruh aplikasi sekaligus.
- Palet warna kategori (untuk grafik dengan banyak seri seperti lapangan
  usaha) memakai mapping tetap lewat `get_category_color_map()` di
  `utils/analysis.py`, supaya warna kategori yang sama selalu konsisten di
  semua chart.
- Untuk deployment (bukan sekadar `python app.py` lokal), gunakan variabel
  `server` yang sudah diekspos di `app.py` (kompatibel dengan gunicorn: 
  `gunicorn app:server`).

## Menambah Analisis Baru

Pola yang dipakai konsisten di semua halaman:
1. Tulis fungsi perhitungan baru di `utils/analysis.py` (menerima DataFrame,
   mengembalikan DataFrame long-format).
2. Tambahkan `dcc.Tab` baru di halaman terkait (`pages/monitoring.py`,
   `pages/wilayah.py`, atau `pages/makro.py`).
3. Tambahkan cabang di fungsi `render_tab()` untuk tab baru tersebut.
4. Tulis callback baru yang memanggil fungsi dari langkah 1 dan mengembalikan
   `plotly` figure (pakai `theme.COLORS` dan `theme.REFERENCE_LINE_STYLE`
   supaya konsisten dengan tema).
