import dash
from dash import html, dcc, callback, Output, Input, State, ctx, no_update

from theme import COLORS
from utils.gemini_assistant import tanya_gemini

dash.register_page(__name__, path="/", name="Beranda")

INITIAL_GREETING = {
    "role": "model",
    "text": (
        "Halo! Saya **Asisten Analis PDRB Kepulauan Riau** berbasis AI.\n\n"
        "Saya telah dibekali basis data resmi BPS mengenai **PDRB Riil (ADHK 2010)**, "
        "**PDRB Per Kapita**, **Sumber Pertumbuhan (SOG)**, serta indikator makroekonomi "
        "(**ICOR, ILOR, Tax Ratio, dan Neraca Perdagangan**) 7 Kabupaten/Kota "
        "periode **2021–2025**.\n\n"
        "Silakan ketik pertanyaan Anda atau gunakan tombol pertanyaan cepat di atas untuk memulai analisis."
    ),
}

QUICK_PROMPTS = {
    "btn-qp-1": "Berikan ringkasan performa ekonomi Kepulauan Riau tahun 2025.",
    "btn-qp-2": "Bandingkan skala dan pertumbuhan ekonomi Kota Batam vs Kabupaten Bintan.",
    "btn-qp-3": "Sektor apa saja yang menjadi pendorong utama pertumbuhan ekonomi Kepri?",
    "btn-qp-4": "Bagaimana efisiensi investasi modal (ICOR) Kepri dari 2021 hingga 2025?",
    "btn-qp-5": "Bagaimana peringkat dan disparitas PDRB per kapita antar 7 kabupaten/kota?",
}


def render_chat_bubbles(history):
    bubbles = []
    for msg in history:
        role = msg.get("role")
        text = msg.get("text", "")
        if role == "user":
            bubbles.append(
                html.Div(
                    className="chat-bubble-user",
                    children=html.P(text, style={"margin": 0}),
                )
            )
        else:
            bubbles.append(
                html.Div(
                    className="chat-bubble-ai",
                    children=[
                        html.Div("Asisten Analis PDRB (BPS Kepri)", className="chat-ai-label"),
                        dcc.Markdown(text, className="chat-ai-markdown"),
                    ],
                )
            )
    return bubbles


layout = html.Div(
    [
        # ── 1. Hero Card Banner Lebar Penuh ───────────────────────────────────
        html.Div(
            className="home-top-row",
            children=[
                html.Div(
                    className="hero-card",
                    children=[
                        html.Div(
                            className="hero-text",
                            children=[
                                html.H2(
                                    "Sistem Informasi & Analisis PDRB Kepulauan Riau",
                                    className="hero-title",
                                ),
                                html.P(
                                    "Pemantauan indikator ekonomi 7 Kabupaten/Kota dan Asisten Analis Cerdas AI terintegrasi (2021–2025).",
                                    className="hero-subtitle",
                                ),
                                html.Div(
                                    className="hero-buttons-container",
                                    children=[
                                        dcc.Link(
                                            "Pantau Perilaku Ekonomi →",
                                            href="/monitoring",
                                            className="hero-button",
                                        ),
                                        dcc.Link(
                                            "Analisis Antar Wilayah & Sektoral →",
                                            href="/wilayah",
                                            className="hero-button-outline",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Img(src="/assets/maskot_1.webp", className="hero-mascot"),
                    ],
                )
            ],
        ),

        # ── 2. Asisten Cerdas AI Chat (Menggantikan Peta Spasial) ─────────────
        html.Div(
            className="ai-chat-card",
            children=[
                # Header Chat
                html.Div(
                    className="ai-chat-header",
                    children=[
                        html.Div([
                            html.H3("Tanya Jawab Analis PDRB Kepri", className="card-title", style={"margin": 0}),
                            html.Span(
                                "Konsultasi cerdas data PDRB, disparitas wilayah, dan indikator makro berbasis data resmi BPS.",
                                style={"fontSize": "12px", "color": COLORS["gray_mid"]},
                            ),
                        ]),
                        html.Div("Gemini AI Active", className="ai-status-badge"),
                    ],
                ),

                # Quick Prompt Pills
                html.Div(
                    className="ai-quick-prompts",
                    children=[
                        html.Span("Topik Cepat:", className="quick-prompt-label"),
                        html.Button("Ringkasan Ekonomi 2025", id="btn-qp-1", className="quick-prompt-pill"),
                        html.Button("Batam vs Bintan", id="btn-qp-2", className="quick-prompt-pill"),
                        html.Button("Sektor Utama", id="btn-qp-3", className="quick-prompt-pill"),
                        html.Button("Efisiensi Investasi (ICOR)", id="btn-qp-4", className="quick-prompt-pill"),
                        html.Button("Peringkat Per Kapita", id="btn-qp-5", className="quick-prompt-pill"),
                    ],
                ),

                # Area Percakapan (Scroll Area)
                dcc.Loading(
                    id="chat-loading",
                    type="dot",
                    color=COLORS["primary"],
                    children=html.Div(
                        id="chat-messages-container",
                        className="chat-scroll-area",
                        children=render_chat_bubbles([INITIAL_GREETING]),
                    ),
                ),

                # Input Bar
                html.Div(
                    className="ai-chat-input-row",
                    children=[
                        dcc.Input(
                            id="chat-user-input",
                            type="text",
                            placeholder="Ketik pertanyaan analisis ekonomi Kepri di sini... (tekan Enter untuk kirim)",
                            className="chat-input-field",
                            debounce=False,
                            n_submit=0,
                        ),
                        html.Button(
                            "Kirim",
                            id="btn-send-chat",
                            className="hero-button",
                            style={"height": "42px", "padding": "0 22px", "flexShrink": 0},
                            n_clicks=0,
                        ),
                        html.Button(
                            "Reset",
                            id="btn-clear-chat",
                            className="hero-button-outline",
                            style={
                                "height": "42px",
                                "padding": "0 16px",
                                "flexShrink": 0,
                                "color": COLORS["primary_dark"],
                                "borderColor": "rgba(23, 58, 102, 0.2)",
                                "backgroundColor": "rgba(23, 58, 102, 0.05)",
                            },
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        ),

        # Store History Percakapan
        dcc.Store(id="chat-history-store", data=[INITIAL_GREETING]),
    ]
)


# ── Callback Interaksi Chat AI ────────────────────────────────────────────────
@callback(
    Output("chat-messages-container", "children"),
    Output("chat-history-store", "data"),
    Output("chat-user-input", "value"),
    Input("btn-send-chat", "n_clicks"),
    Input("chat-user-input", "n_submit"),
    Input("btn-qp-1", "n_clicks"),
    Input("btn-qp-2", "n_clicks"),
    Input("btn-qp-3", "n_clicks"),
    Input("btn-qp-4", "n_clicks"),
    Input("btn-qp-5", "n_clicks"),
    Input("btn-clear-chat", "n_clicks"),
    State("chat-user-input", "value"),
    State("chat-history-store", "data"),
    prevent_initial_call=True,
)
def handle_chat_interaction(
    send_clicks,
    n_submit,
    qp1_clicks,
    qp2_clicks,
    qp3_clicks,
    qp4_clicks,
    qp5_clicks,
    clear_clicks,
    user_input,
    history_data,
):
    triggered_id = ctx.triggered_id
    if not triggered_id:
        return no_update, no_update, no_update

    # Jika tombol Reset diklik
    if triggered_id == "btn-clear-chat":
        reset_history = [INITIAL_GREETING]
        return render_chat_bubbles(reset_history), reset_history, ""

    # Tentukan teks pertanyaan yang diajukan
    if triggered_id in QUICK_PROMPTS:
        prompt_text = QUICK_PROMPTS[triggered_id]
    elif triggered_id in ("btn-send-chat", "chat-user-input"):
        if not user_input or not user_input.strip():
            return no_update, no_update, no_update
        prompt_text = user_input.strip()
    else:
        return no_update, no_update, no_update

    history = history_data if history_data else [INITIAL_GREETING]

    # 1. Masukkan pertanyaan pengguna ke history
    history.append({"role": "user", "text": prompt_text})

    # 2. Panggil API Gemini dengan grounding data
    ai_answer = tanya_gemini(prompt_text, riwayat_chat=history)

    # 3. Masukkan jawaban AI ke history
    history.append({"role": "model", "text": ai_answer})

    # 4. Render tampilan visual chat baru
    new_bubbles = render_chat_bubbles(history)

    return new_bubbles, history, ""


