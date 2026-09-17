"""
Modul Integrasi AI Gemini untuk Asisten Analisis PDRB Kepulauan Riau.
Menggunakan SDK resmi google-genai dan model gemini-3.6-flash.
Data grounded berbasis dataset resmi BPS Kepulauan Riau (2021-2025).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from google import genai
from google.genai import types

# 1. Muat Environment Variable dari .env
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
CANDIDATE_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]


def get_api_key() -> str:
    """Mengambil API key dari environment variables."""
    return os.environ.get("GEMINI_API_KEY", "").strip()


def build_system_knowledge() -> str:
    """Membangun ringkasan fakta data resmi PDRB Kepri sebagai basis pengetahuan grounding."""
    try:
        from utils.data_loader import DATA, PROVINSI_LABEL

        facts = []
        facts.append("=== BASIS DATA RESMI PDRB & MAKRO KEPULAUAN RIAU (BPS, 2021-2025) ===")

        # 1. PDRB Riil ADHK per Kabupaten/Kota
        df_pdrb = DATA.get("pdrb", pd.DataFrame())
        if not df_pdrb.empty and "kab_kota" in df_pdrb.columns:
            pdrb_tot = df_pdrb.groupby(["kab_kota", "tahun"], as_index=False)["adhk"].sum()
            pdrb_2025 = pdrb_tot[pdrb_tot["tahun"] == 2025].sort_values("adhk", ascending=False)
            facts.append("\n[Total PDRB Riil ADHK 2010 Tahun 2025 (Miliar Rp)]:")
            for _, r in pdrb_2025.iterrows():
                facts.append(f"- {r['kab_kota']}: Rp {r['adhk']:,.1f} Miliar")

            # Pertumbuhan Total Kepri
            prov_pdrb = pdrb_tot[pdrb_tot["kab_kota"] == PROVINSI_LABEL].sort_values("tahun")
            if len(prov_pdrb) > 1:
                facts.append("\n[Tren PDRB ADHK Provinsi Kepri]:")
                for _, r in prov_pdrb.iterrows():
                    facts.append(f"- Tahun {r['tahun']}: Rp {r['adhk']:,.1f} Miliar")

        # 2. PDRB Per Kapita
        df_pk = DATA.get("perkapita", pd.DataFrame())
        if not df_pk.empty:
            pk_2025 = df_pk[df_pk["tahun"] == 2025].sort_values("perkapita_adhk_juta", ascending=False)
            facts.append("\n[PDRB Per Kapita Riil ADHK Tahun 2025 (Juta Rp/jiwa)]:")
            for _, r in pk_2025.iterrows():
                facts.append(f"- {r['kab_kota']}: Rp {r['perkapita_adhk_juta']:.2f} Juta/jiwa (Nominal ADHB: Rp {r['perkapita_adhb_juta']:.2f} Juta)")

        # 3. Struktur Sektor Utama (Share terbesar di Kepri)
        facts.append("\n[Struktur 3 Sektor Ekonomi Terbesar Kepri]:")
        facts.append("1. Industri Pengolahan: Kontribusi ~39.4% (Didominasi industri manufaktur di Kota Batam dan Bintan).")
        facts.append("2. Konstruksi: Kontribusi ~19.2% (Pembangunan infrastruktur dan properti kawasan industri).")
        facts.append("3. Perdagangan Besar & Eceran: Kontribusi ~8.9% (Distribusi logistik kepulauan).")

        # 4. Indikator Makroekonomi
        facts.append("\n[Indikator Makro & Efisiensi Ekonomi Kepri]:")
        facts.append("- ICOR (Incremental Capital Output Ratio): Mengalami perbaikan efisiensi signifikan dari 12.02 (2021) menjadi 6.35 (2025). Semakin rendah ICOR, semakin efisien investasi modal fisik (PMTB) menghasilkan tambahan output ekonomi.")
        facts.append("- APC (Average Propensity to Consume): Rata-rata ~41.1% dari pendapatan disposabel dibelanjakan untuk konsumsi rumah tangga, sisanya (~58.9%) berupa tabungan/investasi (APS).")
        facts.append("- Tax Ratio: Rasio penerimaan pajak daerah dan DBH SDA terhadap PDRB berkisar 0.47% - 0.68%.")
        facts.append("- Rasio Perdagangan Internasional (RPI): Kepri konsisten surplus perdagangan luar negeri (RPI positif ~0.06 - 0.09) dengan nilai ekspor mencapai Rp 421,8 T di 2025.")
        facts.append("- Ketimpangan Regional (Indeks Williamson): Berkisar ~0.56, mencerminkan konsentrasi volume ekonomi yang sangat tinggi di Kota Batam (~75% total ekonomi Kepri) dibandingkan daerah kepulauan lainnya.")

        return "\n".join(facts)
    except Exception as e:
        return "Gunakan data resmi Provinsi Kepulauan Riau (2021-2025) untuk menjawab pertanyaan."


def tanya_gemini(pertanyaan: str, riwayat_chat: list = None) -> str:
    """
    Mengirim pertanyaan pengguna ke model Gemini 3.6 Flash dengan System Instruction dan data grounding.
    riwayat_chat: list of dict [{"role": "user"|"model", "text": "..."}]
    """
    api_key = get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return (
            "⚠️ **API Key Gemini belum terkonfigurasi.**\n\n"
            "Silakan masukkan kunci API Anda di file `.env` pada variabel `GEMINI_API_KEY`.\n"
            "Anda dapat memperoleh API Key gratis di [Google AI Studio](https://aistudio.google.com/)."
        )

    try:
        client = genai.Client(api_key=api_key)
        knowledge = build_system_knowledge()

        system_instruction = (
            "Anda adalah Asisten Cerdas dan Analis Ekonomi PDRB Provinsi Kepulauan Riau dari BPS. "
            "Tugas Anda adalah membantu pengguna memahami data PDRB, disparitas wilayah, pertumbuhan ekonomi, "
            "dan indikator makro 7 Kabupaten/Kota di Kepulauan Riau (Karimun, Bintan, Natuna, Lingga, Anambas, Batam, Tanjungpinang) periode 2021–2025.\n\n"
            "PEDOMAN MENJAWAB:\n"
            "1. Jawab secara ringkas, to-the-point, padat, dan akurat (hindari paragraf panjang bertele-tele, utamakan poin-poin singkat atau tabel ringkas).\n"
            "2. Jangan gunakan emotikon atau emoji apapun.\n"
            "3. Gunakan format Markdown: tebalkan angka dan nama wilayah penting.\n"
            "4. Jika pengguna bertanya di luar data ekonomi Kepri, arahkan kembali secara singkat (1 kalimat).\n\n"
            f"{knowledge}"
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            max_output_tokens=1000,
        )

        # Siapkan payload pesan
        contents = []
        if riwayat_chat:
            # Ambil maksimal 6 percakapan terakhir agar konteks terjaga tanpa melebihi batas
            for chat in riwayat_chat[-6:]:
                role = "user" if chat.get("role") == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=chat.get("text", ""))]
                ))

        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=pertanyaan)]
        ))

        last_error = None
        for model_name in CANDIDATE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as model_err:
                last_error = model_err
                # Jika error karena key invalid, tidak perlu dicoba ke model lain
                err_text = str(model_err)
                if "API_KEY_INVALID" in err_text or "400" in err_text:
                    return "Kunci API Gemini tidak valid. Mohon periksa kembali nilai `GEMINI_API_KEY` di file `.env`."
                continue

        if last_error:
            error_str = str(last_error)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return "Batas kuota harian/menit API Gemini telah tercapai (Rate Limit). Mohon tunggu beberapa saat sebelum mencoba kembali."
            return f"Terjadi kendala saat menghubungi Asisten AI: {error_str}"

        return "Maaf, tidak ada respon yang berhasil diperoleh. Silakan coba kembali."

    except Exception as e:
        return f"Terjadi kendala saat memproses permintaan: {e}"
