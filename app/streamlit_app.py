import streamlit as st
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from src.app_pipeline import drive_wise_answer

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="DriveWise AI – Hyundai Automotive Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Brand / Model Data ─────────────────────────────────────
BRANDS = {
    "Hyundai": [
        "Alcazar", "Aura", "Creta", "Creta_EV", "Creta_N_Line",
        "Exter", "Grand_i10_NIOS", "i20", "i20_N_Line",
        "IONIQ5", "Venue", "Venue_N_Line", "Verna"
    ]
}

# ─── Suggested Questions (RAG-answerable from brochure) ─────
# Only questions whose answers are reliably present in Hyundai brochures.
SUGGESTED_QUESTIONS = {
    "Engine & Powertrain": [
        "What engine options are available?",
        "What transmission options are available?",
        "What is the fuel type of this car?",
    ],
    "Safety": [
        "What safety features are available?",
        "How many airbags does it have?",
        "What ADAS features are available?",
    ],
    "Interior & Comfort": [
        "What are the interior features?",
        "Does it have a sunroof?",
        "What is the seating capacity?",
    ],
    "Infotainment & Connectivity": [
        "What infotainment system does it have?",
        "Does it support Android Auto and Apple CarPlay?",
        "What are the connected car features?",
    ],
    "Dimensions & Variants": [
        "What are the dimensions of this car?",
        "What variants are available?",
        "What are the color options?",
    ],
}

# ─── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Root & Body ── */
:root {
    --bg-primary:    #0a0e1a;
    --bg-secondary:  #0f1629;
    --bg-card:       #131929;
    --bg-card-hover: #1a2240;
    --accent:        #3b82f6;
    --accent-glow:   rgba(59,130,246,0.25);
    --accent2:       #6366f1;
    --accent-red:    #ef4444;
    --text-primary:  #f0f4ff;
    --text-secondary:#8b9cc8;
    --text-muted:    #4a5578;
    --border:        rgba(59,130,246,0.15);
    --border-hover:  rgba(59,130,246,0.45);
    --success:       #22c55e;
    --warning:       #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Force dark on all Streamlit wrappers */
.stApp,
.stAppViewContainer,
.stAppViewBlockContainer,
.main,
.main > div,
section[data-testid="stMain"],
div[data-testid="stAppViewContainer"],
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Hero Header ── */
.dw-hero {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1535 40%, #111b42 100%);
    border-bottom: 1px solid var(--border);
    padding: 28px 48px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.dw-hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.dw-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 200px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.dw-logo-wrap {
    display: flex;
    align-items: center;
    gap: 18px;
}
.dw-logo-icon {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    box-shadow: 0 0 24px rgba(99,102,241,0.4);
}
.dw-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #f0f4ff, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.dw-subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 2px 0 0;
    font-weight: 400;
}
.dw-badge {
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(99,102,241,0.2));
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── Main Layout ── */
.dw-main {
    display: flex;
    min-height: calc(100vh - 100px);
}
.dw-sidebar {
    width: 300px;
    min-width: 300px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    padding: 28px 20px;
}
.dw-content {
    flex: 1;
    padding: 32px 40px;
    background: var(--bg-primary);
}

/* ── Section Labels ── */
.dw-section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 10px;
}

/* ── Car Selector Cards ── */
.dw-model-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
}
.dw-model-chip {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12px;
    color: var(--text-secondary);
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
}
.dw-model-chip:hover, .dw-model-chip.active {
    background: var(--bg-card-hover);
    border-color: var(--accent);
    color: var(--text-primary);
}

/* ── Stats Strip ── */
.dw-stats {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
}
.dw-stat {
    flex: 1;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}
.dw-stat::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.dw-stat.blue::before { background: linear-gradient(90deg, #3b82f6, #6366f1); }
.dw-stat.green::before { background: linear-gradient(90deg, #22c55e, #10b981); }
.dw-stat.purple::before { background: linear-gradient(90deg, #a855f7, #6366f1); }
.dw-stat.orange::before { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.dw-stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
}
.dw-stat-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 3px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
.dw-stat-icon {
    position: absolute;
    right: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 22px;
    opacity: 0.35;
}

/* ── Chat Input Area ── */
.dw-input-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.dw-input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
}

/* ── Suggested Pill Buttons ── */
.dw-suggestions-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.dw-sugg-category {
    font-size: 11px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 0 0 8px;
}
.dw-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}
.dw-pill {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: #93c5fd;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}
.dw-pill:hover {
    background: rgba(59,130,246,0.18);
    border-color: rgba(59,130,246,0.5);
    color: #bfdbfe;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.15);
}

/* ── Answer Card ── */
.dw-answer-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    margin-top: 20px;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.4s ease;
}
.dw-answer-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #6366f1, #a855f7);
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.dw-answer-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.dw-answer-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
}
.dw-answer-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}
.dw-answer-text {
    font-size: 14px;
    line-height: 1.75;
    color: #c8d3f5;
    white-space: pre-wrap;
}
.dw-source-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 11px;
    color: #93c5fd;
    margin: 4px 4px 0 0;
}

/* ── Streamlit overrides ── */
div[data-testid="stSelectbox"] > div > div {
    background: #111829 !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
}
div[data-testid="stTextInput"] > div > div > input {
    background: #111829 !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.45) !important;
}
div[data-testid="stSpinner"] > div {
    color: var(--accent) !important;
}
div[data-testid="stAlert"] {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 10px !important;
    color: #fcd34d !important;
}
label[data-testid="stWidgetLabel"] p {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 3px; }

/* ── Sidebar overrides ── */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ────────────────────────────────────────────
st.markdown("""
<div class="dw-hero">
    <div class="dw-logo-wrap">
        <div class="dw-logo-icon">🚗</div>
        <div>
            <div class="dw-title">DriveWise AI</div>
            <div class="dw-subtitle">Hyundai Automotive Intelligence Platform</div>
        </div>
    </div>
    <div class="dw-badge">⚡ RAG-Powered · Gemini · ChromaDB</div>
</div>
""", unsafe_allow_html=True)

# ─── Stats Strip ────────────────────────────────────────────
st.markdown("""
<div style="padding: 20px 40px 0;">
<div class="dw-stats">
    <div class="dw-stat blue">
        <div class="dw-stat-value">13</div>
        <div class="dw-stat-label">Car Models</div>
        <div class="dw-stat-icon">🚗</div>
    </div>
    <div class="dw-stat green">
        <div class="dw-stat-value">70+</div>
        <div class="dw-stat-label">Safety Features Tracked</div>
        <div class="dw-stat-icon">🛡️</div>
    </div>
    <div class="dw-stat purple">
        <div class="dw-stat-value">RAG</div>
        <div class="dw-stat-label">Brochure-Grounded AI</div>
        <div class="dw-stat-icon">🧠</div>
    </div>
    <div class="dw-stat orange">
        <div class="dw-stat-value">Real-time</div>
        <div class="dw-stat-label">Semantic Retrieval</div>
        <div class="dw-stat-icon">⚡</div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# ─── Two-Column Layout ───────────────────────────────────────
col_left, col_right = st.columns([1, 2], gap="large")

with col_left:
    st.markdown("<div style='padding: 0 0 0 40px'>", unsafe_allow_html=True)

    # Brand & Model selectors
    st.markdown("<div class='dw-section-label' style='margin-top:8px'>Select Vehicle</div>", unsafe_allow_html=True)

    brand = st.selectbox("Brand", list(BRANDS.keys()), label_visibility="collapsed")
    model = st.selectbox("Car Model", BRANDS[brand], label_visibility="collapsed")

    # Model info card
    model_display = model.replace("_", " ")
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(99,102,241,0.08));
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 12px;
        padding: 16px 18px;
        margin-top: 12px;
    ">
        <div style="font-size:11px; color: #6366f1; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">Selected Vehicle</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700; color:#f0f4ff;">{model_display}</div>
        <div style="font-size:12px; color:#8b9cc8; margin-top:2px;">{brand} · Official Brochure Data</div>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown("""
    <div style="margin-top: 24px;">
        <div class="dw-section-label">How It Works</div>
        <div style="display:flex; flex-direction:column; gap:10px; margin-top:10px;">
            <div style="display:flex; align-items:flex-start; gap:10px;">
                <div style="width:22px;height:22px;background:linear-gradient(135deg,#3b82f6,#6366f1);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;">1</div>
                <div style="font-size:12px; color:#8b9cc8; line-height:1.5;">Select your Hyundai model from the list</div>
            </div>
            <div style="display:flex; align-items:flex-start; gap:10px;">
                <div style="width:22px;height:22px;background:linear-gradient(135deg,#6366f1,#a855f7);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;">2</div>
                <div style="font-size:12px; color:#8b9cc8; line-height:1.5;">Pick a suggested question or type your own</div>
            </div>
            <div style="display:flex; align-items:flex-start; gap:10px;">
                <div style="width:22px;height:22px;background:linear-gradient(135deg,#a855f7,#ec4899);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;">3</div>
                <div style="font-size:12px; color:#8b9cc8; line-height:1.5;">AI retrieves from official brochure & generates grounded answer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='padding: 0 40px 0 0'>", unsafe_allow_html=True)

    # ── Suggested Questions ──────────────────────────────────
    st.markdown("""
    <div class="dw-suggestions-wrap">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:16px;">
            <span style="font-size:16px;">💡</span>
            <span style="font-family:'Space Grotesk',sans-serif; font-size:14px; font-weight:600; color:#f0f4ff;">Suggested Questions</span>
            <span style="font-size:11px; color:#4a5578; margin-left:4px;">Click to autofill</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Autofill: pills write directly into the text_input's own key ──
    # Initialise the shared key that both pills and text_input use
    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    # Render pill buttons per category
    for category, questions in SUGGESTED_QUESTIONS.items():
        st.markdown(f'<div class="dw-sugg-category">{category}</div>', unsafe_allow_html=True)

        cols = st.columns(len(questions))
        for i, q in enumerate(questions):
            with cols[i]:
                if st.button(q, key=f"pill_{category}_{i}", use_container_width=True):
                    # Write directly into the text_input's key so it picks it up
                    st.session_state.question_input = q
                    st.rerun()   # force re-render so input shows the filled value

        st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Ask Input ────────────────────────────────────────────
    st.markdown("""
    <div style="
        background: var(--bg-card);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 16px;
        position: relative;
    ">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(99,102,241,0.5),transparent);"></div>
        <div style="font-size:13px; font-weight:600; color:#8b9cc8; margin-bottom:12px; letter-spacing:0.3px;">✏️ Ask your question</div>
    """, unsafe_allow_html=True)

    # key="question_input" — same key pills write to, so autofill works
    question = st.text_input(
        "question",
        placeholder="e.g. What safety features are available in this model?",
        label_visibility="collapsed",
        key="question_input"
    )

    btn_col, hint_col = st.columns([1, 3])
    with btn_col:
        ask_clicked = st.button("🔍 Ask DriveWise", use_container_width=True)
    with hint_col:
        st.markdown("""
        <div style="font-size:11px; color:#4a5578; padding-top:10px; line-height:1.5;">
            Answers sourced exclusively from official Hyundai brochures · No hallucination
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Answer Area ──────────────────────────────────────────
    if ask_clicked:
        if question:
            with st.spinner(""):
                st.markdown("""
                <div style="text-align:center; padding:16px; color:#8b9cc8; font-size:13px;">
                    🔍 Searching brochure · Re-ranking results · Generating answer...
                </div>
                """, unsafe_allow_html=True)
                response = drive_wise_answer(brand, model, question)

            # Parse answer vs sources
            if "\n\nSources:" in response:
                answer_text, sources_raw = response.split("\n\nSources:", 1)
            else:
                answer_text = response
                sources_raw = ""

            answer_text = answer_text.strip()

            # Render answer card
            st.markdown(f"""
            <div class="dw-answer-card">
                <div class="dw-answer-header">
                    <div class="dw-answer-icon">🤖</div>
                    <div>
                        <div class="dw-answer-title">DriveWise Answer</div>
                        <div style="font-size:11px; color:#4a5578; margin-top:1px;">Based on official {brand} {model_display} brochure</div>
                    </div>
                </div>
                <div class="dw-answer-text">{answer_text}</div>
            """, unsafe_allow_html=True)

            # Parse & render sources
            if sources_raw.strip():
                st.markdown("""
                <div style="margin-top:20px; padding-top:16px; border-top:1px solid rgba(59,130,246,0.12);">
                    <div style="font-size:11px; font-weight:700; color:#4a5578; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">📚 Source References</div>
                    <div style="display:flex; flex-wrap:wrap; gap:6px;">
                """, unsafe_allow_html=True)

                lines = [l.strip() for l in sources_raw.strip().split("\n") if l.strip()]
                for line in lines:
                    # Clean up emoji and format as chip
                    clean = line.replace("📄", "").replace("📌", "").replace("📄", "").strip()
                    if clean:
                        st.markdown(f'<div class="dw-source-chip">📄 {clean}</div>', unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="
                background: rgba(245,158,11,0.08);
                border: 1px solid rgba(245,158,11,0.25);
                border-radius: 12px;
                padding: 14px 18px;
                margin-top: 8px;
                font-size: 13px;
                color: #fcd34d;
            ">
                ⚠️ Please enter a question or select one from the suggestions above.
            </div>
            """, unsafe_allow_html=True)

    elif not ask_clicked and "last_response" not in st.session_state:
        # Welcome state
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(59,130,246,0.05), rgba(99,102,241,0.05));
            border: 1px dashed rgba(99,102,241,0.25);
            border-radius: 16px;
            padding: 36px;
            text-align: center;
            margin-top: 8px;
        ">
            <div style="font-size:40px; margin-bottom:12px;">🚗</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:16px; font-weight:600; color:#c8d3f5; margin-bottom:8px;">
                Ready to answer your questions about the {model_display}
            </div>
            <div style="font-size:12px; color:#4a5578; line-height:1.6;">
                Select a suggested question above or type your own.<br>
                All answers are grounded in official Hyundai brochure data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────
st.markdown("""
<div style="
    background: var(--bg-secondary);
    border-top: 1px solid rgba(59,130,246,0.1);
    padding: 16px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 20px;
">
    <div style="font-size:12px; color:#4a5578;">
        🚗 <strong style="color:#6b7db3;">DriveWise AI</strong> · Built with Streamlit · Powered by Gemini + ChromaDB
    </div>
    <div style="font-size:11px; color:#4a5578;">
        Answers sourced exclusively from official Hyundai brochures
    </div>
</div>
""", unsafe_allow_html=True)