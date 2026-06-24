import streamlit as st
# call the detect_and_explain from the script
from inference_ import detect_and_explain

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard – Email Subject Detector",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def _interface(subject: str) -> tuple[str, str]:
    """
    Thin wrapper that mirrors the original Gradio callback signature.
    Keeps the function name identical for compatibility with any
    existing references or test harnesses.

    Args:
        subject (str): Email subject line entered by the user.

    Returns:
        tuple[str, str]: (verdict, explanation) from detect_and_explain.
    """
    verdict, explanation, risk_score = detect_and_explain(subject)
    return verdict, explanation, risk_score


# ──────────────────────────────────────────────────────────────
# CUSTOM CSS  – brand colours, typography, component overrides
# ──────────────────────────────────────────────────────────────
def inject_custom_css() -> None:

    st.markdown(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&display=swap');

        :root {
            --blue-dark: #1a6fb5;
            --blue-mid: #155a96;
            --bg: #0D1B3E;
            --surface: #122260;
            --surface-2: #1A2F78;
            --text-primary: #EEF1FB;
            --text-secondary: #A8B4D8;
            --radius: 14px;
        }

        html, body, [class*="css"] {
            font-family: 'Sora', sans-serif !important;
            background-color: var(--bg) !important;
            color: var(--text-primary) !important;
        }

        .stApp {
            background-color: var(--bg) !important;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .block-container {
            max-width: 780px !important;
            padding: 2.5rem 2rem 4rem !important;
        }

        /* HERO SECTION */

        .hero-banner {
            background: linear-gradient(135deg, var(--blue-dark) 0%, var(--surface-2) 100%);
            border: 1px solid var(--blue-mid);
            border-radius: var(--radius);
            padding: 2.2rem;
            margin-bottom: 2rem;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }

        .hero-sub {
            font-size: 0.95rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* LABELS */

        .section-label {
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #A8B4D8;
            margin-bottom: 0.45rem;
        }

        /* TEXT AREA */

        textarea, input[type="text"], .stTextInput input {

            background-color: var(--surface) !important;
            border: 1px solid var(--blue-mid) !important;
            border-radius: var(--radius) !important;

            color: white !important;

            font-size: 0.95rem !important;
            padding: 0.8rem 1rem !important;
        }

        textarea:focus, input[type="text"]:focus {
            border-color: #1a6fb5 !important;
            box-shadow: none !important;
        }

        /* BUTTON */

        div.stButton > button {

            width: 100%;

            background-color: #1a6fb5 !important;
            color: white !important;

            border: none !important;
            border-radius: var(--radius) !important;

            padding: 0.75rem 1.5rem !important;

            font-weight: 700 !important;
            font-size: 1rem !important;
        }

        div.stButton > button:hover {
            background-color: #155a96 !important;
            color: white !important;
        }

        /* RESULT CARD */

        .result-card {

            background: var(--surface);

            border-radius: var(--radius);

            padding: 1.4rem 1.6rem;

            margin-top: 0.5rem;

            border-left: 5px solid #1a6fb5;
        }

        .result-card.phishing {
            border-left: 5px solid #dc3545;
        }

        .result-card.legitimate {
            border-left: 5px solid #28a745;
        }

        .verdict-pill {

            display: inline-block;

            font-size: 1.1rem;
            font-weight: 700;

            padding: 0.35rem 1rem;

            border-radius: 999px;

            margin-bottom: 0.5rem;
        }

        .verdict-pill.phishing {
            background: rgba(220,53,69,0.15);
            color: #ff6b81;
        }

        .verdict-pill.legitimate {
            background: rgba(40,167,69,0.15);
            color: #51cf66;
        }

        /* EXPLANATION */

        .explanation-box {

            background: rgba(0,0,0,0.2);

            border-radius: 10px;

            padding: 1rem;

            margin-top: 1rem;

            color: var(--text-secondary);

            line-height: 1.7;

            border-left: 3px solid var(--blue-mid);
        }

        /* EXAMPLE BUTTONS */

        .example-chip {
            background: var(--surface-2);
            border: 1px solid var(--blue-mid);
            border-radius: 999px;
            padding: 0.35rem 0.9rem;
            color: var(--text-secondary);
        }

        hr {
            border: none;
            border-top: 1px solid var(--surface-2);
            margin: 1.8rem 0;
        }

        .footer-bar {
            margin-top: 3rem;
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-secondary);
            opacity: 0.6;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────
# COMPONENT HELPERS
# ──────────────────────────────────────────────────────────────

def render_hero() -> None:
    """Render the branded hero/header banner at the top of the page."""
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">🛡️ PhishGuard</div>
            <p class="hero-sub">
                Paste any email subject line and get an instant AI-powered verdict.<br>
                Identify phishing attempts before they reach your inbox.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(verdict: str, explanation: str, risk_score: float) -> None:
    """
    Render the classification result as styled HTML cards.

    Args:
        verdict     (str): Classification label returned by _interface.
        explanation (str): Detailed reasoning returned by _interface.
    """
    # Determine card style based on verdict content
    is_phishing = "PHISHING" in verdict.upper()
    card_class   = "phishing" if is_phishing else "legitimate"
    pill_class   = "phishing" if is_phishing else "legitimate"

    st.markdown(
        f"""
        <div class="result-card {card_class}">
            <div class="section-label">Classification</div>
            <span class="verdict-pill {pill_class}">{verdict}</span>
            <div style="margin-top:10px; font-size:0.95rem; color:#A8B4D8;">
                Risk Score: <b>{risk_score}%</b>
            </div>
            <div class="section-label" style="margin-top:1.1rem;">Analysis</div>
            <div class="explanation-box">{explanation}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_examples() -> list[str]:
    """
    Display clickable example subject lines and return the user's selection.

    Returns:
        list[str]: The example strings (used for populating the text area
                   via Streamlit session state).
    """
    examples = [
        "Urgent: Action Required - Verify your account immediately!!!",
        "Weekly team meeting notes - April 17",
        "Your account has been suspended - Click here to reactivate",
        "Invoice #478292 - Payment overdue",
    ]

    st.markdown('<div class="section-label">Try an example</div>', unsafe_allow_html=True)

    # Render one Streamlit button per example in a column grid
    cols = st.columns(len(examples))
    for col, example in zip(cols, examples):
        with col:
            short_label = example[:28] + "…" if len(example) > 28 else example
            if st.button(short_label, key=f"ex_{example[:20]}", help=example):
                st.session_state["subject_input"] = example

    return examples


def render_footer() -> None:
    """Render a minimal branded footer."""
    st.markdown(
        """
        <div class="footer-bar">
            PhishGuard · Built with Streamlit · For demonstration purposes only
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# MAIN APPLICATION ENTRY POINT
# ──────────────────────────────────────────────────────────────

def main() -> None:
    """
    Main Streamlit application runner.
    Orchestrates layout, state, and event handling.
    """
    # ── Apply brand styles ────────────────────────────────────
    inject_custom_css()

    # ── Initialize session state ──────────────────────────────
    if "subject_input" not in st.session_state:
        st.session_state["subject_input"] = ""
    if "result" not in st.session_state:
        st.session_state["result"] = None   # holds (verdict, explanation) tuple

    # ── Hero banner ───────────────────────────────────────────
    render_hero()

    # ── Example chips (must appear before text_area so state is set first) ──
    render_examples()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Subject input ─────────────────────────────────────────
    st.markdown('<div class="section-label">Email subject line</div>', unsafe_allow_html=True)
    subject = st.text_area(
        label="Email subject line",           # hidden by CSS label suppression
        label_visibility="collapsed",
        placeholder="e.g. Urgent: Verify your account immediately!!!",
        height=90,
        key="subject_input",
    )

    # ── Analyse button ────────────────────────────────────────
    st.write("")   # vertical spacer
    analyse_clicked = st.button("🔍  Analyse Subject", key="analyse_btn")

    # ── Classification logic ──────────────────────────────────
    if analyse_clicked:
        if not subject.strip():
            st.warning("Please enter an email subject line before analysing.")
        else:
            with st.spinner("Analysing subject line…"):
                # Call the preserved wrapper
                verdict, explanation, risk_score = _interface(subject)
                st.session_state["result"] = (verdict, explanation, risk_score)

    # ── Result display ────────────────────────────────────────
    if st.session_state["result"] is not None:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Result</div>', unsafe_allow_html=True)
        render_result(*st.session_state["result"])

    # ── Footer ────────────────────────────────────────────────
    render_footer()


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()