from io import BytesIO

import pandas as pd
import plotly.express as px
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


def _read_dataframe(filename, content):
    buffer = BytesIO(content)
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return pd.read_csv(buffer)
    if lower_name.endswith(".xlsx"):
        return pd.read_excel(buffer)
    if lower_name.endswith(".json"):
        return pd.read_json(buffer)
    raise ValueError("Unsupported file type.")


def _clean_dataframe(df):
    cleaned = df.drop_duplicates().copy()
    for column in cleaned.columns:
        if not cleaned[column].isna().any():
            continue

        if pd.api.types.is_numeric_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())
        else:
            mode = cleaned[column].mode(dropna=True)
            fallback = mode.iloc[0] if not mode.empty else "Unknown"
            cleaned[column] = cleaned[column].fillna(fallback)

    return cleaned


def show_process_visual_page():
    st.markdown("<div style='font-size:2rem;font-weight:800;margin-top:6px' class='page-vibrant-title'>Process & Visualize</div>", unsafe_allow_html=True)

    st.caption("Clean an uploaded file, inspect it, and download the result.")

    auth_token = st.session_state.get("auth_token")
    user_email = st.session_state.get("user_email")

    if not auth_token or not user_email:
        st.error("Please log in first.")
        st.stop()

    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        files_response = requests.get(
            f"{BACKEND_URL}/files/{user_email}",
            headers=headers,
            params={"page": 1, "per_page": 200},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not reach backend: {exc}")
        return

    if files_response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        st.session_state.clear()
        st.rerun()
        return

    if files_response.status_code != 200:
        st.error(_error_message(files_response, "Could not load uploaded files."))
        return

    response_data = files_response.json()
    data = response_data.get("data", response_data)
    filenames = data.get("files", [])
    if not filenames:
        st.info("Upload a CSV, Excel, or JSON file first.")
        return

    filename = st.selectbox("Select a file", filenames)
    if st.session_state.get("processed_filename") != filename:
        st.session_state.pop("processed_df", None)

    if st.button("Load and Process"):
        try:
            file_response = requests.get(
                f"{BACKEND_URL}/get_file_data",
                params={"filename": filename},
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")
            return

        if file_response.status_code != 200:
            st.error(_error_message(file_response, "Could not download file."))
            return

        try:
            df = _read_dataframe(filename, file_response.content)
            cleaned = _clean_dataframe(df)
        except Exception as exc:
            st.error(f"Could not process file: {exc}")
            return

        st.session_state["processed_df"] = cleaned
        st.session_state["processed_filename"] = filename
        st.success(f"Processed {len(cleaned)} rows and {len(cleaned.columns)} columns.")

    processed = st.session_state.get("processed_df")
    if processed is None:
        return

    st.subheader("Cleaned Data Preview")
    st.dataframe(processed.head(50), use_container_width=True)

    numeric_columns = processed.select_dtypes(include="number").columns.tolist()
    text_columns = processed.select_dtypes(exclude="number").columns.tolist()

    theme_template = "plotly_dark" if st.session_state.get("dark_mode", True) else "plotly_white"

    if numeric_columns:
        column = st.selectbox("Numeric column", numeric_columns)
        chart = px.histogram(processed, x=column, title=f"Distribution of {column}", template=theme_template)
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No numeric columns found for histogram charts.")

    if text_columns:
        category = st.selectbox("Category column", text_columns)
        top_values = processed[category].astype(str).value_counts().head(10).reset_index()
        top_values.columns = [category, "count"]
        chart = px.bar(top_values, x=category, y="count", title=f"Top values in {category}", template=theme_template)
        chart.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, use_container_width=True)

    csv_data = processed.to_csv(index=False).encode("utf-8")
    st.download_button("Download Cleaned CSV", csv_data, file_name="cleaned_data.csv", mime="text/csv")
