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


def show_signup_page():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown(
        """
        <section class="auth-header-centered">
            <p class="eyebrow">Create your account</p>
            <h1>Start your business data workspace</h1>
            <p>
                Upload, clean, and visualize your datasets securely.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 1.8, 1])

    with form_col:
        st.markdown('<div class="auth-form-title">New Account</div>', unsafe_allow_html=True)
        with st.form("signup_form"):
            full_name = st.text_input(
                "Full name",
                placeholder="Enter your full name, e.g. Alex Morgan",
            )
            email = st.text_input(
                "Email address",
                placeholder="Enter your email, e.g. alex@company.com",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password (min 12 chars)",
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        st.markdown(
            """
            <div style="text-align: center; margin-top: 1.25rem;">
                <span style="color: var(--ink); font-size: 0.95rem; font-weight: 500;">
                    Already have an account? Open <strong style="color: #1f6feb; font-weight: 700;">Login</strong> from the sidebar.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if not submitted:
        return

    if not full_name or not email or not password:
        st.warning("All fields are required.")
        return
    if len(password) < 12:
        st.warning("Password must be at least 12 characters.")
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/signup",
            json={"full_name": full_name.strip(), "email": email.strip(), "password": password},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach backend: {exc}")
        return

    if response.status_code == 201:
        st.success("Signup successful. You can log in now.")
    else:
        st.error(_error_message(response, "Signup failed."))
