import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)


backend_url = os.getenv("BACKEND_URL")
if not backend_url:
    try:
        import streamlit as st
        backend_url = st.secrets.get("BACKEND_URL")
    except Exception:
        backend_url = None

BACKEND_URL = (backend_url or "https://dataflow-business-automation-backend.onrender.com").rstrip("/")
REQUEST_TIMEOUT = 30
