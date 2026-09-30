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
    if dark_mode:
        st.markdown(
            """
            <style>
            :root {
                --bg: #0b0f19;
                --surface: #111827;
                --ink: #f8fafc;
                --muted: #94a3b8;
                --line: rgba(255, 255, 255, 0.08);
                --primary: #3b82f6;
                --primary-dark: #2563eb;
                --auth-bg: #111827;
                --auth-border: rgba(255, 255, 255, 0.08);
                --auth-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                --auth-title: #ffffff;
                --auth-subtitle: #94a3b8;
                --input-bg: #0b0f19;
            }

            html, body, .stApp {
                background: #0b0f19 !important;
                color: #f8fafc !important;
            }

            .stMarkdown, .stText, .stCaption {
                color: #f8fafc !important;
            }

            /* Auth Header & Card */
            .auth-card-header h1 {
                color: #ffffff !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
            }

            .auth-card-header p {
                color: #94a3b8 !important;
            }

            div[data-testid="stForm"] {
                background: #111827 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
            }

            [data-testid="stTextInput"] input {
                background: #0b0f19 !important;
                color: #f8fafc !important;
                border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
            }

            [data-testid="stTextInput"] input:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
            }

            [data-testid="stTextInput"] label {
                color: #e2e8f0 !important;
            }

            .auth-switch-prompt span {
                color: #94a3b8 !important;
            }

            /* Hero Section */
            .hero {
                background: linear-gradient(135deg, #131c2e 0%, #0d1522 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
            }

            .hero h1 {
                color: #ffffff !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
            }

            .hero__copy {
                color: #94a3b8 !important;
            }

            .eyebrow {
                color: #38bdf8 !important;
                background: rgba(56, 189, 248, 0.12) !important;
                border: 1px solid rgba(56, 189, 248, 0.25) !important;
                padding: 4px 14px !important;
                border-radius: 9999px !important;
                display: inline-block !important;
            }

            .hero__panel {
                background: rgba(11, 15, 25, 0.95) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
            }

            .hero__panel .panel-row {
                border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
            }

            .hero__panel .panel-row span {
                color: #94a3b8 !important;
            }

            .hero__panel .panel-row strong {
                color: #60a5fa !important;
            }

            /* Stat & Step Cards */
            .stat, .step {
                background: linear-gradient(180deg, #151f32 0%, #111827 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
            }

            .stat span, .step p {
                color: #94a3b8 !important;
            }

            .stat strong, .step h3 {
                color: #ffffff !important;
            }

            .section-title {
                color: #ffffff !important;
                border-left: 3px solid #3b82f6 !important;
                padding-left: 10px !important;
            }

            .step-index {
                background: rgba(59, 130, 246, 0.15) !important;
                color: #60a5fa !important;
            }

            /* Tables & lists */
            .latest-file {
                background: #111827 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }

            .latest-file span, .file-list-time, .file-list-header {
                color: #94a3b8 !important;
            }

            .latest-file strong, .file-list-name {
                color: #f8fafc !important;
            }

            [data-testid="stSidebar"] {
                background: #070a11 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            :root {
                --bg: #f8fafc;
                --surface: #ffffff;
                --ink: #0f172a;
                --muted: #64748b;
                --line: #e2e8f0;
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --auth-bg: #ffffff;
                --auth-border: #e2e8f0;
                --auth-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
                --auth-title: #0f172a;
                --auth-subtitle: #475569;
                --input-bg: #ffffff;
            }

            html, body, .stApp {
                background: #f8fafc !important;
                color: #0f172a !important;
            }

            .stMarkdown, .stText, .stCaption {
                color: #0f172a !important;
            }

            /* Auth Header & Card */
            .auth-card-header h1 {
                color: #0f172a !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
            }

            .auth-card-header p {
                color: #475569 !important;
            }

            div[data-testid="stForm"] {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08) !important;
            }

            [data-testid="stTextInput"] input {
                background: #ffffff !important;
                color: #0f172a !important;
                border: 1.5px solid #cbd5e1 !important;
            }

            [data-testid="stTextInput"] input:focus {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
            }

            [data-testid="stTextInput"] label {
                color: #1e293b !important;
                font-weight: 600 !important;
            }

            .auth-switch-prompt span {
                color: #475569 !important;
            }

            /* Hero Section */
            .hero {
                background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(16, 185, 129, 0.05)), #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06) !important;
            }

            .hero h1 {
                color: #0f172a !important;
                font-weight: 800 !important;
                letter-spacing: -0.02em !important;
            }

            .hero__copy {
                color: #475569 !important;
            }

            .eyebrow {
                color: #0284c7 !important;
                background: rgba(2, 132, 199, 0.08) !important;
                border: 1px solid rgba(2, 132, 199, 0.2) !important;
                padding: 4px 14px !important;
                border-radius: 9999px !important;
                display: inline-block !important;
            }

            .hero__panel {
                background: #0f172a !important;
                border: 1px solid rgba(15, 23, 42, 0.2) !important;
                color: #f8fafc !important;
            }

            .hero__panel .panel-row {
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }

            .hero__panel .panel-row span {
                color: #94a3b8 !important;
            }

            .hero__panel .panel-row strong {
                color: #38bdf8 !important;
            }

            /* Stat & Step Cards */
            .stat, .step {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 12px !important;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04) !important;
            }

            .stat span, .step p {
                color: #64748b !important;
            }

            .stat strong, .step h3 {
                color: #0f172a !important;
            }

            .section-title {
                color: #0f172a !important;
                border-left: 3px solid #2563eb !important;
                padding-left: 10px !important;
            }

            .step-index {
                background: rgba(37, 99, 235, 0.1) !important;
                color: #2563eb !important;
            }

            /* Tables & lists */
            .latest-file {
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
            }

            .latest-file span, .file-list-time, .file-list-header {
                color: #64748b !important;
            }

            .latest-file strong, .file-list-name {
                color: #0f172a !important;
            }

            [data-testid="stSidebar"] {
                background: #0f172a !important;
                border-right: 1px solid #1e293b !important;
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
                <p class="eyebrow">Business Data Entry Automation</p>
                <h1>Upload, clean, and understand business data in one workspace.</h1>
                <p class="hero__copy">
                    Bring CSV, Excel, or JSON files into a simple workflow for previewing,
                    storing, cleaning, visualizing, and downloading analysis-ready data.
                </p>
            </div>
            <div class="hero__panel">
                <div class="panel-row">
                    <span>Accepted files</span>
                    <strong>CSV, XLSX, JSON</strong>
                </div>
                <div class="panel-row">
                    <span>Cleaning</span>
                    <strong>Missing values, duplicates</strong>
                </div>
                <div class="panel-row">
                    <span>Outputs</span>
                    <strong>Charts, previews, CSV export</strong>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    stat_1, stat_2, stat_3 = st.columns(3)
    with stat_1:
        st.markdown('<div class="stat"><span>Workflow</span><strong>3 steps</strong></div>', unsafe_allow_html=True)
    with stat_2:
        st.markdown('<div class="stat"><span>Storage</span><strong>User based</strong></div>', unsafe_allow_html=True)
    with stat_3:
        st.markdown('<div class="stat"><span>Analysis</span><strong>Interactive</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Workflow</div>', unsafe_allow_html=True)
    step_1, step_2, step_3 = st.columns(3)
    with step_1:
        st.markdown(
            '<div class="step"><span class="step-index">01</span><h3>Upload</h3><p>Select a business dataset and preview rows before sending it to the API.</p></div>',
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
