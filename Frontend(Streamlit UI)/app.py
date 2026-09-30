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
        # VoiceStudio Midnight Obsidian & Neon Coral (Dark Mode)
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

            /* Hero Section */
            .hero {
                background: linear-gradient(135deg, #181520 0%, #121017 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 25px 60px rgba(0, 0, 0, 0.55) !important;
            }

            .hero h1 {
                color: #FFFFFF !important;
            }

            .hero__copy {
                color: #9CA3AF !important;
            }

            .btn-coral {
                background: #FA6682 !important;
                color: #0F0E13 !important;
            }

            .btn-ghost {
                background: #1E1C24 !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
            }

            .hero__panel {
                background: #131118 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }

            .panel-row {
                border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
            }

            .panel-row strong {
                color: #FFFFFF !important;
            }

            /* Spec Rows */
            .spec-row {
                border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
            }

            .spec-val {
                color: #D1D5DB !important;
            }

            /* Stat & Step Cards */
            .stat, .step {
                background: #17151E !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }

            .stat span, .step p {
                color: #9CA3AF !important;
            }

            .stat strong, .step h3 {
                color: #FFFFFF !important;
            }

            .section-title {
                color: #FFFFFF !important;
            }

            /* Auth Forms */
            .auth-card-header h1 {
                color: #FFFFFF !important;
            }

            .auth-card-header p {
                color: #9CA3AF !important;
            }

            div[data-testid="stForm"] {
                background: #17151E !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6) !important;
            }

            [data-testid="stTextInput"] input {
                background: #121017 !important;
                color: #FFFFFF !important;
                border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
            }

            [data-testid="stTextInput"] input:focus {
                border-color: #FA6682 !important;
                box-shadow: 0 0 0 3px rgba(250, 102, 130, 0.25) !important;
            }

            [data-testid="stTextInput"] label {
                color: #E5E7EB !important;
            }

            .auth-switch-prompt span {
                color: #9CA3AF !important;
            }

            /* Buttons */
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

            /* Sidebar */
            [data-testid="stSidebar"] {
                background: #121117 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
            }

            /* File card in dark mode */
            .file-card {
                background: #17151E !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 10px !important;
                padding: 12px 16px !important;
                margin-bottom: 6px !important;
            }

            .file-card-name {
                color: #FFFFFF !important;
                font-size: 0.95rem !important;
                display: block !important;
                word-break: break-all !important;
            }

            .file-card-time {
                color: #9CA3AF !important;
                font-size: 0.8rem !important;
                margin-top: 2px !important;
                display: block !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        # VoiceStudio Coral Light Mode
        st.markdown(
            """
            <style>
            :root {
                --bg: #FAF9FB;
                --surface: #FFFFFF;
                --surface-card: #FFFFFF;
                --surface-hover: #F6F3F7;
                --coral: #FA6682;
                --coral-light: #FF7D99;
                --coral-dark: #E24B68;
                --ink: #131118;
                --text-white: #131118;
                --text-muted: #5C5868;
                --line: #E8E4EB;
                --primary: #FA6682;
                --primary-dark: #E24B68;
                --auth-bg: #FFFFFF;
                --auth-border: #E8E4EB;
                --auth-shadow: 0 20px 45px rgba(25, 20, 30, 0.06);
                --auth-title: #131118;
                --auth-subtitle: #5C5868;
                --input-bg: #FFFFFF;
                --input-border: #DCD7E1;
            }

            html, body, .stApp {
                background: #FAF9FB !important;
                color: #131118 !important;
            }

            header[data-testid="stHeader"] {
                background: #FAF9FB !important;
            }

            .stMarkdown, .stText, .stCaption {
                color: #131118 !important;
            }

            h1, h2, h3, h4, h5, h6 {
                color: #131118 !important;
            }

            .page-vibrant-title {
                color: #131118 !important;
            }

            /* Hero Section */
            .hero {
                background: linear-gradient(135deg, #FFFFFF 0%, #FBF9FB 100%) !important;
                border: 1px solid #E8E4EB !important;
                box-shadow: 0 20px 50px rgba(25, 20, 30, 0.06) !important;
            }

            .hero h1 {
                color: #131118 !important;
            }

            .hero__copy {
                color: #5C5868 !important;
            }

            .btn-coral {
                background: #FA6682 !important;
                color: #FFFFFF !important;
                box-shadow: 0 8px 20px rgba(250, 102, 130, 0.28) !important;
            }

            .btn-ghost {
                background: #F1EDF3 !important;
                color: #131118 !important;
                border: 1px solid #DCD7E1 !important;
            }

            .hero__panel {
                background: #F9F6F9 !important;
                border: 1px solid #E8E4EB !important;
                box-shadow: 0 10px 25px rgba(25, 20, 30, 0.04) !important;
            }

            .panel-row {
                border-bottom: 1px solid #EAE5ED !important;
            }

            .panel-row strong {
                color: #131118 !important;
            }

            .panel-tag {
                color: #FA6682 !important;
            }

            /* Spec Rows */
            .spec-row {
                border-bottom: 1px solid #ECE7EE !important;
            }

            .spec-tag {
                color: #FA6682 !important;
            }

            .spec-val {
                color: #373344 !important;
            }

            /* Stat & Step Cards */
            .stat, .step {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                box-shadow: 0 8px 24px rgba(25, 20, 30, 0.04) !important;
            }

            .stat span {
                color: #6B6678 !important;
            }

            .stat strong {
                color: #131118 !important;
            }

            .step h3 {
                color: #131118 !important;
            }

            .step p {
                color: #5C5868 !important;
            }

            .step-index {
                background: rgba(250, 102, 130, 0.12) !important;
                color: #FA6682 !important;
            }

            .section-title {
                color: #131118 !important;
            }

            /* Auth Forms */
            .auth-card-header h1 {
                color: #131118 !important;
            }

            .auth-card-header p {
                color: #5C5868 !important;
            }

            div[data-testid="stForm"] {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                box-shadow: 0 20px 45px rgba(25, 20, 30, 0.06) !important;
            }

            [data-testid="stTextInput"] input {
                background: #FFFFFF !important;
                color: #131118 !important;
                border: 1.5px solid #DCD7E1 !important;
            }

            [data-testid="stTextInput"] input:focus {
                border-color: #FA6682 !important;
                box-shadow: 0 0 0 3px rgba(250, 102, 130, 0.2) !important;
            }

            [data-testid="stTextInput"] label,
            [data-testid="stSelectbox"] label,
            [data-testid="stFileUploader"] label {
                color: #131118 !important;
                font-weight: 600 !important;
            }

            .auth-switch-prompt span {
                color: #5C5868 !important;
            }

            /* Buttons */
            .stButton > button[kind="primary"],
            [data-testid="stFormSubmitButton"] button {
                background: #FA6682 !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                border: none !important;
                border-radius: 8px !important;
                box-shadow: 0 8px 22px rgba(250, 102, 130, 0.28) !important;
            }

            .stButton > button[kind="primary"]:hover,
            [data-testid="stFormSubmitButton"] button:hover {
                background: #FF7D99 !important;
                box-shadow: 0 12px 28px rgba(250, 102, 130, 0.4) !important;
                transform: translateY(-2px) !important;
            }

            .stButton > button[kind="secondary"],
            .stButton > button {
                background: #F3EEF4 !important;
                color: #131118 !important;
                border: 1px solid #DCD7E1 !important;
                border-radius: 8px !important;
            }

            .stButton > button[kind="secondary"]:hover,
            .stButton > button:hover {
                border-color: #FA6682 !important;
                color: #FA6682 !important;
                background: rgba(250, 102, 130, 0.08) !important;
            }

            /* Download Button */
            .stDownloadButton > button {
                background: #FA6682 !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                border: none !important;
                border-radius: 8px !important;
                box-shadow: 0 8px 22px rgba(250, 102, 130, 0.28) !important;
            }

            .stDownloadButton > button:hover {
                background: #FF7D99 !important;
                box-shadow: 0 12px 28px rgba(250, 102, 130, 0.4) !important;
                color: #FFFFFF !important;
                transform: translateY(-2px) !important;
            }

            /* Table & Lists */
            .latest-file {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
            }

            .latest-file span {
                color: #FA6682 !important;
            }

            .latest-file strong {
                color: #131118 !important;
            }

            .file-list-header {
                color: #FA6682 !important;
                border-bottom: 1px solid #E8E4EB !important;
            }

            .file-list-name {
                color: #131118 !important;
                border-bottom: 1px solid #ECE7EE !important;
            }

            .file-list-time {
                color: #5C5868 !important;
                border-bottom: 1px solid #ECE7EE !important;
            }

            /* Selectbox & Dropdowns */
            [data-testid="stSelectbox"] > div > div {
                background: #FFFFFF !important;
                color: #131118 !important;
                border: 1.5px solid #DCD7E1 !important;
                border-radius: 8px !important;
            }

            [data-testid="stSelectbox"] svg {
                fill: #131118 !important;
            }

            /* File Uploader Dropzone */
            [data-testid="stFileUploadDropzone"] {
                background: #FFFFFF !important;
                border: 1.5px dashed #DCD7E1 !important;
                border-radius: 12px !important;
            }

            [data-testid="stFileUploadDropzone"]:hover {
                border-color: #FA6682 !important;
            }

            [data-testid="stFileUploadDropzone"] span,
            [data-testid="stFileUploadDropzone"] small {
                color: #5C5868 !important;
            }

            [data-testid="stFileUploadDropzone"] button {
                background: #F3EEF4 !important;
                color: #131118 !important;
                border: 1px solid #DCD7E1 !important;
            }

            /* Dataframe */
            .stDataFrame {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                border-radius: 10px !important;
            }

            /* Expanders */
            [data-testid="stExpander"] {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                border-radius: 10px !important;
            }

            [data-testid="stExpander"] details summary {
                color: #131118 !important;
                font-weight: 600 !important;
            }

            [data-testid="stExpander"] details summary svg {
                fill: #131118 !important;
            }

            /* Metrics */
            [data-testid="stMetric"] {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                border-radius: 12px !important;
                padding: 16px !important;
            }

            [data-testid="stMetricLabel"] {
                color: #5C5868 !important;
            }

            [data-testid="stMetricValue"] {
                color: #131118 !important;
            }

            /* Toggles & Checkboxes */
            [data-testid="stCheckbox"] label,
            [data-testid="stToggle"] label {
                color: #131118 !important;
            }

            hr {
                border-color: #E8E4EB !important;
            }

            /* Sidebar Light Mode */
            [data-testid="stSidebar"] {
                background: #F7F5F8 !important;
                border-right: 1px solid #E8E4EB !important;
            }

            [data-testid="stSidebar"] * {
                color: #131118;
            }

            [data-testid="stSidebar"] .sidebar-title {
                color: #131118 !important;
            }

            [data-testid="stSidebar"] .sidebar-subtitle {
                color: #5C5868 !important;
            }

            [data-testid="stSidebar"] .sidebar-logo {
                background: linear-gradient(135deg, #FA6682, #E24B68) !important;
                color: #FFFFFF !important;
            }

            [data-testid="stSidebar"] .sidebar-status {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                box-shadow: 0 4px 12px rgba(25, 20, 30, 0.03) !important;
            }

            [data-testid="stSidebar"] .sidebar-status strong {
                color: #131118 !important;
            }

            [data-testid="stSidebar"] .sidebar-status small {
                color: #5C5868 !important;
            }

            [data-testid="stSidebar"] .status-dot {
                background: #FA6682 !important;
                box-shadow: 0 0 0 4px rgba(250, 102, 130, 0.2) !important;
            }

            [data-testid="stSidebar"] .sidebar-status--active .status-dot {
                background: #22c55e !important;
                box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2) !important;
            }

            [data-testid="stSidebar"] .sidebar-section {
                color: #FA6682 !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                background: #FFFFFF !important;
                color: #131118 !important;
                border: 1px solid #E8E4EB !important;
                font-weight: 650 !important;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                border-color: #FA6682 !important;
                background: rgba(250, 102, 130, 0.08) !important;
                color: #FA6682 !important;
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background: #FA6682 !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                border: none !important;
                box-shadow: 0 8px 20px rgba(250, 102, 130, 0.28) !important;
            }

            .sidebar-footer div strong {
                color: #131118 !important;
            }

            .sidebar-footer div span {
                color: #5C5868 !important;
            }

            /* File card in light mode */
            .file-card {
                background: #FFFFFF !important;
                border: 1px solid #E8E4EB !important;
                border-radius: 10px !important;
                padding: 12px 16px !important;
                margin-bottom: 6px !important;
                box-shadow: 0 4px 14px rgba(25, 20, 30, 0.03) !important;
            }

            .file-card-name {
                color: #131118 !important;
                font-size: 0.95rem !important;
                display: block !important;
                word-break: break-all !important;
            }

            .file-card-time {
                color: #5C5868 !important;
                font-size: 0.8rem !important;
                margin-top: 2px !important;
                display: block !important;
            }

            /* Mobile Hamburger in light mode */
            [data-testid="stSidebarCollapsedControl"] button {
                background: #FFFFFF !important;
                border: 1px solid #DCD7E1 !important;
                color: #FA6682 !important;
                box-shadow: 0 2px 8px rgba(25, 20, 30, 0.06) !important;
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
