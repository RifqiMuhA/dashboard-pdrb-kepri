"""
Modul Integrasi AI Gemini untuk Asisten Analisis PDRB Kepulauan Riau.
Menggunakan Google Generative Language REST API bawaan Python (urllib).
Bebas dependensi eksternal untuk menjamin kompatibilitas 100% di PythonAnywhere.
Data grounded berbasis dataset resmi BPS Kepulauan Riau (2021-2025).
"""

import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import pandas as pd

# 1. Muat Environment Variable dari .env secara aman
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / ".env"


def _load_env_safely():
    try:
        from dotenv import load_dotenv

        if _ENV_PATH.exists():
            load_dotenv(_ENV_PATH)
    except ImportError:
        # Fallback manual parser tanpa butuh paket python-dotenv
        if _ENV_PATH.exists():
            try:
                with open(_ENV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


_load_env_safely()

CANDIDATE_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash"]


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
                facts.append(
                    f"- {r['kab_kota']}: Rp {r['perkapita_adhk_juta']:.2f} Juta/jiwa (Nominal ADHB: Rp {r['perkapita_adhb_juta']:.2f} Juta)"
                )

        # 3. Struktur Sektor Utama (Share terbesar di Kepri)
        facts.append("\n[Struktur 3 Sektor Ekonomi Terbesar Kepri]:")
        facts.append(
            "1. Industri Pengolahan: Kontribusi ~39.4% (Didominasi industri manufaktur di Kota Batam dan Bintan)."
        )
        facts.append("2. Konstruksi: Kontribusi ~19.2% (Pembangunan infrastruktur dan properti kawasan industri).")
        facts.append("3. Perdagangan Besar & Eceran: Kontribusi ~8.9% (Distribusi logistik kepulauan).")

        # 4. Indikator Makroekonomi
        facts.append("\n[Indikator Makro & Efisiensi Ekonomi Kepri]:")
        facts.append(
            "- ICOR (Incremental Capital Output Ratio): Mengalami perbaikan efisiensi signifikan dari 12.02 (2021) menjadi 6.35 (2025). Semakin rendah ICOR, semakin efisien investasi modal fisik (PMTB) menghasilkan tambahan output ekonomi."
        )
        facts.append(
            "- APC (Average Propensity to Consume): Rata-rata ~41.1% dari pendapatan disposabel dibelanjakan untuk konsumsi rumah tangga, sisanya (~58.9%) berupa tabungan/investasi (APS)."
        )
        facts.append(
            "- Tax Ratio: Rasio penerimaan pajak daerah dan DBH SDA terhadap PDRB berkisar 0.47% - 0.68%."
        )
        facts.append(
            "- Rasio Perdagangan Internasional (RPI): Kepri konsisten surplus perdagangan luar negeri (RPI positif ~0.06 - 0.09) dengan nilai ekspor mencapai Rp 421,8 T di 2025."
        )
        facts.append(
            "- Ketimpangan Regional (Indeks Williamson): Berkisar ~0.56, mencerminkan konsentrasi volume ekonomi yang sangat tinggi di Kota Batam (~75% total ekonomi Kepri) dibandingkan daerah kepulauan lainnya."
        )

        return "\n".join(facts)
    except Exception:
        return "Gunakan data resmi Provinsi Kepulauan Riau (2021-2025) untuk menjawab pertanyaan."


def tanya_gemini(pertanyaan: str, riwayat_chat: list = None) -> str:
    """
    Mengirim pertanyaan pengguna ke endpoint REST Gemini dengan System Instruction dan data grounding.
    Menggunakan urllib bawaan tanpa butuh paket google-genai eksternal.
    riwayat_chat: list of dict [{"role": "user"|"model", "text": "..."}]
    """
    api_key = get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return (
            "API Key Gemini belum terkonfigurasi.\n\n"
            "Silakan masukkan kunci API Anda di file `.env` pada variabel `GEMINI_API_KEY`."
        )

    try:
        knowledge = build_system_knowledge()

        system_instruction = (
            "Anda adalah Asisten Analis Ekonomi PDRB Provinsi Kepulauan Riau dari BPS. "
            "Tugas Anda adalah membantu pengguna memahami data PDRB, disparitas wilayah, pertumbuhan ekonomi, "
            "dan indikator makro 7 Kabupaten/Kota di Kepulauan Riau (Karimun, Bintan, Natuna, Lingga, Anambas, Batam, Tanjungpinang) periode 2021–2025.\n\n"
            "PEDOMAN MENJAWAB:\n"
            "1. Jawab secara ringkas, to-the-point, padat, dan akurat (hindari paragraf panjang bertele-tele, utamakan poin-poin singkat atau tabel ringkas).\n"
            "2. Jangan gunakan emotikon atau emoji apapun.\n"
            "3. Gunakan format Markdown: tebalkan angka dan nama wilayah penting.\n"
            "4. Jika pengguna bertanya di luar data ekonomi Kepri, arahkan kembali secara singkat (1 kalimat).\n\n"
            f"{knowledge}"
        )

        # Siapkan payload percakapan
        contents = []
        if riwayat_chat:
            for chat in riwayat_chat[-6:]:
                role = "user" if chat.get("role") == "user" else "model"
                text = chat.get("text", "")
                if text:
                    contents.append({
                        "role": role,
                        "parts": [{"text": text}],
                    })

        contents.append({
            "role": "user",
            "parts": [{"text": pertanyaan}],
        })

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 3000,
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            },
        }

        last_error = None
        for model_name in CANDIDATE_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            
            # Coba kirim request (dengan fallback jika thinkingConfig tidak didukung)
            for current_payload in [
                payload,
                {
                    "system_instruction": payload["system_instruction"],
                    "contents": payload["contents"],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 3000,
                    },
                },
            ]:
                data_bytes = json.dumps(current_payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=35) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                        candidates = resp_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            text_chunks = [p.get("text", "") for p in parts if "text" in p]
                            full_text = "".join(text_chunks).strip()
                            if full_text:
                                return full_text
                    # Jika berhasil, keluar dari loop payload
                    break
                except urllib.error.HTTPError as http_err:
                    last_error = http_err
                    err_code = http_err.code
                    try:
                        err_body = http_err.read().decode("utf-8")
                    except Exception:
                        err_body = ""

                    if err_code == 400:
                        if "API_KEY_INVALID" in err_body:
                            return "Kunci API Gemini tidak valid. Mohon periksa kembali nilai `GEMINI_API_KEY` di file `.env`."
                        # Coba payload berikutnya tanpa thinkingConfig
                        continue
                    if err_code == 429 or "RESOURCE_EXHAUSTED" in err_body:
                        return "Batas kuota API Gemini telah tercapai. Mohon tunggu beberapa saat sebelum mencoba kembali."
                    # 503 / 404 -> coba model kandidat berikutnya
                    break
                except Exception as conn_err:
                    last_error = conn_err
                    break


        if last_error:
            return f"Terjadi kendala saat menghubungi Asisten AI: {last_error}"

        return "Maaf, tidak ada respon yang berhasil diperoleh. Silakan coba kembali."

    except Exception as e:
        return f"Terjadi kendala saat memproses permintaan: {e}"

