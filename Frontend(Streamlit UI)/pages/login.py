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
        <div class="auth-card-header">
            <div class="auth-logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
            </div>
            <h1>Welcome back</h1>
            <p>Enter your credentials to access your business datasets</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 1.8, 1])

    with form_col:
        with st.form("login_form"):
            email = st.text_input(
                "Email address",
                placeholder="name@company.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••••••",
            )
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        st.markdown(
            """
            <div class="auth-switch-prompt">
                <span>Don't have an account?</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Create new account", key="switch_to_signup", use_container_width=True, type="secondary"):
            st.session_state["current_page"] = "Signup"
            st.rerun()

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
