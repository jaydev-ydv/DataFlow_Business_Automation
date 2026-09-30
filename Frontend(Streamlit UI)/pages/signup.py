import time
import requests
import streamlit as st

from config import BACKEND_URL, REQUEST_TIMEOUT


def _error_message(response, fallback):
    try:
        body = response.json()
        error = body.get("error", fallback)
        if isinstance(error, dict):
            msg = error.get("message", fallback)
            details = error.get("details")
            if isinstance(details, dict):
                detail_lines = [f"• {v}" for v in details.values() if v]
                if detail_lines:
                    return f"{msg}\n\n" + "\n".join(detail_lines)
            elif isinstance(details, list):
                return f"{msg}: {', '.join(str(d) for d in details)}"
            return msg
        return str(error)
    except Exception:
        return fallback


def show_signup_page():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="auth-card-header">
            <div class="auth-logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="8.5" cy="7" r="4"></circle>
                    <line x1="20" y1="8" x2="20" y2="14"></line>
                    <line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
            </div>
            <h1>Create an account</h1>
            <p>Start managing and automating your business data workflow</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        with st.form("signup_form"):
            full_name = st.text_input(
                "Full name",
                placeholder="Alex Morgan",
            )
            email = st.text_input(
                "Email address",
                placeholder="name@company.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 characters (letters & numbers)",
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        st.markdown(
            """
            <div class="auth-switch-prompt">
                <span>Already have an account?</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Sign in instead", key="switch_to_login", use_container_width=True, type="secondary"):
            st.session_state["current_page"] = "Login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if not submitted:
        return

    if not full_name or not email or not password:
        st.warning("All fields are required.")
        return
    if len(password) < 8:
        st.warning("Password must be at least 8 characters long.")
        return

    with st.spinner("Creating your account..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/signup",
                json={"full_name": full_name.strip(), "email": email.strip(), "password": password},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach backend ({BACKEND_URL}): {exc}")
            return

    if response.status_code == 201:
        st.success("Account created successfully! Redirecting to login...")
        time.sleep(1.2)
        st.session_state["current_page"] = "Login"
        st.rerun()
    else:
        st.error(_error_message(response, "Signup failed."))
