import time

import pandas as pd
import requests
import streamlit as st

from config import BACKEND_URL, REQUEST_TIMEOUT

MAX_UPLOAD_BYTES = 16 * 1024 * 1024  # keep in sync with backend MAX_CONTENT_LENGTH



def _read_preview(uploaded_file):
    uploaded_file.seek(0)
    lower_name = uploaded_file.name.lower()
    if lower_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if lower_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if lower_name.endswith(".json"):
        return pd.read_json(uploaded_file)
    raise ValueError("Unsupported file type.")


def _error_message(response, fallback):
    try:
        error = response.json().get("error", fallback)
        if isinstance(error, dict):
            return error.get("message", fallback)
        return error
    except ValueError:
        return fallback


def _request_with_retry(method, url, *, headers=None, files=None, params=None, json=None, timeout=REQUEST_TIMEOUT, max_attempts=3):
    """Small retry wrapper for transient errors."""
    session = requests.Session()
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.request(
                method,
                url,
                headers=headers,
                files=files,
                params=params,
                json=json,
                timeout=timeout,
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                # retryable
                retry_after = resp.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else min(2 ** (attempt - 1), 8)
                time.sleep(sleep_s)
                continue
            return resp
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            time.sleep(min(2 ** (attempt - 1), 8))
    # If we exhausted attempts
    if last_exc:
        raise last_exc
    raise requests.exceptions.RequestException("Request failed after retries")


def show_upload_page():
    st.markdown("<div style='font-size:2rem;font-weight:800;margin-top:6px' class='page-vibrant-title'>Upload File</div>", unsafe_allow_html=True)

    st.caption("Preview a CSV, Excel, or JSON file before storing it.")

    auth_token = st.session_state.get("auth_token")
    if not auth_token:
        st.error("Please log in first.")
        st.stop()

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])
    if uploaded_file is None:
        st.info("Supported formats: CSV, XLSX, JSON.")
        return

    file_size = getattr(uploaded_file, "size", None)
    if file_size is not None and file_size > MAX_UPLOAD_BYTES:
        st.error(f"File is too large. Max allowed size is 16MB (your file: {file_size/1024/1024:.2f}MB).")
        return


    with st.spinner("Reading file preview..."):
        try:
            df = _read_preview(uploaded_file)
        except Exception as exc:
            st.error(f"Failed to preview file: {exc}")
            return


    st.success(f"Selected `{uploaded_file.name}` with {len(df)} rows and {len(df.columns)} columns.")
    with st.expander("Preview", expanded=True):
        st.dataframe(df.head(25), use_container_width=True)

    left, right = st.columns([2, 1])
    with left:
        st.write("Columns")
        st.write(list(df.columns))
    with right:
        upload_clicked = st.button("Upload File", use_container_width=True)

    if not upload_clicked:
        return

    with st.spinner("Uploading file..."):
        try:
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = _request_with_retry(
                "POST",
                f"{BACKEND_URL}/upload",
                headers=headers,
                files=files,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Upload failed (network). Could not reach backend: {exc}")
            return


    if response.status_code == 201:
        st.success("File uploaded successfully.")
    elif response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        st.session_state.clear()
        st.rerun()
    else:
        st.error(_error_message(response, "Upload failed."))
