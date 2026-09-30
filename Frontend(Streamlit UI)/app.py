from pathlib import Path

import streamlit as st

from pages.history import show_history_page
from pages.login import show_login_page
from pages.process_visual import show_process_visual_page
from pages.signup import show_signup_page
from pages.upload import show_upload_page


AUTH_PAGES = ["Login", "Signup"]
WORKSPACE_PAGES = ["Home", "Upload File", "Recent Files", "Process & Visualize"]


def load_css():
    css_path = Path(__file__).parent / "static" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def apply_dark_mode(dark_mode: bool):
    # VoiceStudio midnight obsidian & neon coral theme
    st.markdown(
        """
        <style>
        :root {
            --bg: #0F0E13;
            --surface: #17151E;
            --surface-card: #1B1924;
            --coral: #FA6682;
            --coral-light: #FF7D99;
            --coral-dark: #E24B68;
            --ink: #FFFFFF;
            --text-white: #FFFFFF;
            --text-muted: #9CA3AF;
            --line: rgba(255, 255, 255, 0.08);
            --primary: #FA6682;
            --primary-dark: #E24B68;
            --auth-bg: #17151E;
            --auth-border: rgba(255, 255, 255, 0.08);
            --input-bg: #121017;
            --input-border: rgba(255, 255, 255, 0.12);
        }

        html, body, .stApp {
            background: #0F0E13 !important;
            color: #FFFFFF !important;
        }

        .stMarkdown, .stText, .stCaption {
            color: #FFFFFF !important;
        }

        /* VoiceStudio Buttons */
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background: #FA6682 !important;
            color: #0F0E13 !important;
            font-weight: 800 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 22px rgba(250, 102, 130, 0.35) !important;
        }

        .stButton > button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background: #FF7D99 !important;
            box-shadow: 0 12px 28px rgba(250, 102, 130, 0.5) !important;
            transform: translateY(-2px) !important;
        }

        .stButton > button[kind="secondary"] {
            background: #1E1C24 !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 8px !important;
        }

        .stButton > button[kind="secondary"]:hover {
            border-color: rgba(250, 102, 130, 0.5) !important;
            color: #FA6682 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



def show_home_page():
    st.markdown(
        """
        <section class="hero">
            <div class="hero__content">
                <div class="eyebrow-container">
                    <span class="eyebrow-line"></span>
                    <span class="eyebrow">Workflows</span>
                </div>
                <h1>DataFlow Studio</h1>
                <p class="hero__copy">
                    Drop in a CSV, Excel, or JSON business dataset and DataFlow mirrors, cleans, and visualizes it — automated pipelines run in seconds with zero manual configuration.
                </p>
                <div class="hero-actions">
                    <a href="#workspace" class="btn-coral">Start Workflow</a>
                    <a href="https://github.com/jaydev-ydv/DataFlow_Business_Automation" target="_blank" class="btn-ghost">Documentation</a>
                </div>
            </div>
            <div class="hero__panel">
                <div class="panel-row">
                    <span class="panel-tag">ACCEPTED FILES</span>
                    <strong>CSV, XLSX, JSON</strong>
                </div>
                <div class="panel-row">
                    <span class="panel-tag">CLEANING</span>
                    <strong>Missing values, duplicates</strong>
                </div>
                <div class="panel-row">
                    <span class="panel-tag">OUTPUTS</span>
                    <strong>Interactive charts, CSV export</strong>
                </div>
                <div class="panel-row">
                    <span class="panel-tag">ENGINE</span>
                    <strong>PostgreSQL & Gunicorn</strong>
                </div>
            </div>
        </section>

        <div class="spec-container">
            <div class="spec-row">
                <div class="spec-tag">INPUT</div>
                <div class="spec-val">Drop in any business dataset — CSV, Excel spreadsheet, or JSON exports up to 16MB.</div>
            </div>
            <div class="spec-row">
                <div class="spec-tag">PROCESSING</div>
                <div class="spec-val">Automatic deduplication and column-aware numeric median & categorical mode imputation.</div>
            </div>
            <div class="spec-row">
                <div class="spec-tag">OUTPUT</div>
                <div class="spec-val">Instant distribution histograms, top category bar charts, and one-click clean CSV export.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Workflow Pipeline</div>', unsafe_allow_html=True)
    step_1, step_2, step_3 = st.columns(3)
    with step_1:
        st.markdown(
            '<div class="step"><span class="step-index">01</span><h3>Upload</h3><p>Select a business dataset and preview rows before sending it to the processing API.</p></div>',
            unsafe_allow_html=True,
        )
    with step_2:
        st.markdown(
            '<div class="step"><span class="step-index">02</span><h3>Clean</h3><p>Remove duplicate records and fill missing values using column-aware defaults.</p></div>',
            unsafe_allow_html=True,
        )
    with step_3:
        st.markdown(
            '<div class="step"><span class="step-index">03</span><h3>Visualize</h3><p>Explore numeric distributions and top category values, then export the cleaned CSV.</p></div>',
            unsafe_allow_html=True,
        )

    st.info("Start with Signup or Login, then upload a file from the sidebar.")


st.set_page_config(page_title="DataFlow Business Automation", layout="wide")
load_css()

# Dark mode (UI only)
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

dark_mode = st.sidebar.toggle("Dark mode", value=st.session_state["dark_mode"], help="Toggle dark theme")
st.session_state["dark_mode"] = dark_mode
apply_dark_mode(dark_mode)


is_logged_in = bool(st.session_state.get("auth_token"))
user_name = st.session_state.get("user_name", "User")
user_email = st.session_state.get("user_email", "")

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-logo">BA</div>
        <div>
            <div class="sidebar-title">DataFlow Business Automation</div>
            <div class="sidebar-subtitle">Data cleaning workspace</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

st.sidebar.markdown('<div class="sidebar-section sidebar-section--top">Account</div>', unsafe_allow_html=True)
if is_logged_in:
    if st.sidebar.button("Logout", key="nav_logout_top", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.session_state["current_page"] = "Home"
        st.rerun()
else:
    login_col, signup_col = st.sidebar.columns(2)
    with login_col:
        login_type = "primary" if st.session_state["current_page"] == "Login" else "secondary"
        if st.button("Login", key="nav_login_top", use_container_width=True, type=login_type):
            st.session_state["current_page"] = "Login"
            st.rerun()
    with signup_col:
        signup_type = "primary" if st.session_state["current_page"] == "Signup" else "secondary"
        if st.button("Signup", key="nav_signup_top", use_container_width=True, type=signup_type):
            st.session_state["current_page"] = "Signup"
            st.rerun()

if is_logged_in:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-status sidebar-status--active">
            <span class="status-dot"></span>
            <div>
                <strong>{user_name}</strong>
                <small>{user_email}</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        """
        <div class="sidebar-status">
            <span class="status-dot"></span>
            <div>
                <strong>Not signed in</strong>
                <small>Login to upload and analyze files</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)
for page_name in WORKSPACE_PAGES:
    is_current = st.session_state["current_page"] == page_name
    button_type = "primary" if is_current else "secondary"
    if st.sidebar.button(page_name, key=f"nav_{page_name}", use_container_width=True, type=button_type):
        st.session_state["current_page"] = page_name
        st.rerun()

page = st.session_state["current_page"]

if page == "Home":
    show_home_page()
elif page == "Login":
    show_login_page()
elif page == "Signup":
    show_signup_page()
elif page == "Upload File":
    show_upload_page()
elif page == "Recent Files":
    show_history_page()
elif page == "Process & Visualize":
    show_process_visual_page()

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        <div><strong>Secure</strong><span>JWT protected sessions</span></div>
        <div><strong>Fast</strong><span>Preview before upload</span></div>
        <div><strong>Smart</strong><span>Clean and visualize</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)
