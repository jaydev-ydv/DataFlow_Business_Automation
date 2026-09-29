from html import escape

import time

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


def _delete_file(file_id, headers):
    with st.spinner("Deleting file..."):
        try:
            response = _request_with_retry(
                "DELETE",
                f"{BACKEND_URL}/files/{file_id}",
                headers=headers,
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")
            return


    if response.status_code == 200:
        st.success("File deleted successfully.")
        st.rerun()
    elif response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        st.session_state.clear()
        st.rerun()
    else:
        st.error(_error_message(response, "Failed to delete file."))


def _request_with_retry(method, url, *, headers=None, params=None, timeout=REQUEST_TIMEOUT, max_attempts=3):
    session = requests.Session()
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = session.request(method, url, headers=headers, params=params, timeout=timeout)
            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = resp.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else min(2 ** (attempt - 1), 8)
                time.sleep(sleep_s)
                continue
            return resp
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            time.sleep(min(2 ** (attempt - 1), 8))
    if last_exc:
        raise last_exc
    raise requests.exceptions.RequestException("Request failed after retries")


def show_history_page():
    st.markdown("<div style='font-size:2rem;font-weight:800;margin-top:6px' class='page-vibrant-title'>Recent Uploaded Files</div>", unsafe_allow_html=True)

    st.caption("Files saved under your account.")


    auth_token = st.session_state.get("auth_token")
    if not auth_token:
        st.error("Please log in first.")
        st.stop()

    headers = {"Authorization": f"Bearer {auth_token}"}
    page = st.session_state.get("history_page", 1)
    per_page = 10

    with st.spinner("Loading your upload history..."):
        try:
            response = _request_with_retry(
                "GET",
                f"{BACKEND_URL}/history",
                headers=headers,
                params={"page": page, "per_page": per_page},
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")
            return


    if response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        st.session_state.clear()
        st.rerun()
        return

    if response.status_code != 200:
        st.error(_error_message(response, "Failed to fetch upload history."))
        return

    response_data = response.json()
    data = response_data.get("data", response_data)
    files = data.get("uploaded_files", [])
    pagination = data.get("pagination", {})
    if not files:
        st.info("No uploaded files yet.")
        return

    total_files = pagination.get("total", len(files))
    current_page = pagination.get("page", page)
    total_pages = pagination.get("pages", 1)
    st.success(f"Found {total_files} uploaded files.")

    # Reset view pagination when API page changes
    if st.session_state.get("history_page") != current_page:
        st.session_state["history_ui_page"] = 1


    latest_file = files[0]
    latest_filename = escape(str(latest_file["filename"]))
    latest_col, delete_latest_col = st.columns([2.7, 1], vertical_alignment="center")
    with latest_col:
        st.markdown(
            f"""
            <div class="latest-file">
                <span>Latest uploaded file</span>
                <strong>{latest_filename}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with delete_latest_col:
        if st.button("Delete Latest", key="delete_latest_file", use_container_width=True):
            _delete_file(latest_file["id"], headers)

    st.markdown(
        """
        <div class="file-list-header">
            <span>Filename</span>
            <span>Upload Time</span>
            <span>Action</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # UI-side pagination for better table UX within the backend page payload
    ui_page_size = st.selectbox("Rows per view", [5, 10, 15], index=1, key="history_ui_page_size")
    ui_total = len(files)
    ui_pages = max((ui_total + ui_page_size - 1) // ui_page_size, 1)
    ui_page = st.session_state.get("history_ui_page", 1)
    ui_page = min(max(ui_page, 1), ui_pages)

    ui_start = (ui_page - 1) * ui_page_size
    ui_end = min(ui_start + ui_page_size, ui_total)
    ui_files = files[ui_start:ui_end]

    for file in ui_files:
        filename = escape(str(file["filename"]))
        upload_time = escape(str(file["upload_time"]))
        name_col, time_col, action_col = st.columns([2.3, 1.25, 0.7], vertical_alignment="center")
        with name_col:
            st.markdown(f'<div class="file-list-name">{filename}</div>', unsafe_allow_html=True)
        with time_col:
            st.markdown(f'<div class="file-list-time">{upload_time}</div>', unsafe_allow_html=True)
        with action_col:
            if st.button("Delete", key=f"delete_file_{file['id']}", use_container_width=True):
                _delete_file(file["id"], headers)

    ui_prev_col, ui_page_col, ui_next_col = st.columns([1, 2, 1], vertical_alignment="center")
    with ui_prev_col:
        if st.button("View Previous", disabled=(ui_page <= 1), use_container_width=True):
            st.session_state["history_ui_page"] = max(ui_page - 1, 1)
            st.rerun()
    with ui_page_col:
        st.caption(f"View {ui_page} of {ui_pages}")
    with ui_next_col:
        if st.button("View Next", disabled=(ui_page >= ui_pages), use_container_width=True):
            st.session_state["history_ui_page"] = ui_page + 1
            st.rerun()


    # Keep backend pagination controls (switching API pages)
    prev_col, page_col, next_col = st.columns([1, 2, 1], vertical_alignment="center")

    with prev_col:
        if st.button("Previous (API)", disabled=not pagination.get("has_prev"), use_container_width=True):
            st.session_state["history_page"] = max(current_page - 1, 1)
            st.rerun()
    with page_col:
        st.caption(f"API Page {current_page} of {max(total_pages, 1)}")
    with next_col:
        if st.button("Next (API)", disabled=not pagination.get("has_next"), use_container_width=True):
            st.session_state["history_page"] = current_page + 1
            st.rerun()

