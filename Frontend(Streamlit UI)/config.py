import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")
REQUEST_TIMEOUT = 15
