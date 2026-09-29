import requests
import streamlit as st

from config import BACKEND_URL, REQUEST_TIMEOUT


def _error_message(response, fallback):
    try:
        error = response.json().get("error", fallback)
        if isinstance(error, dict):
            return error.get("message", fallback)
        return error
    except ValueError:
        return fallback


def show_login_page():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown(
        """
        <section class="auth-header-centered">
            <p class="eyebrow">Welcome back</p>
            <h1>Login to your workspace</h1>
            <p>
                Access your uploaded files, history, and visualizations.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 1.8, 1])

    with form_col:
        st.markdown('<div class="auth-form-title">Account Access</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input(
                "Email address",
                placeholder="Enter your registered email, e.g. alex@company.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your account password",
            )
            submitted = st.form_submit_button("Login", use_container_width=True)

        st.markdown(
            """
            <div style="text-align: center; margin-top: 1.25rem;">
                <span style="color: var(--ink); font-size: 0.95rem; font-weight: 500;">
                    New here? Open <strong style="color: #1f6feb; font-weight: 700;">Signup</strong> from the sidebar.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if not submitted:
        return

    if not email or not password:
        st.warning("Please enter email and password.")
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": email.strip(), "password": password},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach backend: {exc}")
        return

    if response.status_code == 200:
        response_data = response.json()
        data = response_data.get("data", response_data)
        st.session_state["auth_token"] = data["token"]
        st.session_state["user_id"] = data["user"]["id"]
        st.session_state["user_email"] = data["user"]["email"]
        st.session_state["user_name"] = data["user"].get("full_name", "User")
        st.success("Login successful.")
        st.rerun()
    else:
        st.error(_error_message(response, "Invalid email or password."))
