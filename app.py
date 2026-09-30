import os
import sys
from pathlib import Path

# Add frontend directory to Python path
FRONTEND_DIR = Path(__file__).resolve().parent / "Frontend(Streamlit UI)"
sys.path.insert(0, str(FRONTEND_DIR))
os.chdir(FRONTEND_DIR)

# Run the frontend Streamlit application
app_path = FRONTEND_DIR / "app.py"
globals()["__file__"] = str(app_path)
with open(app_path, "r", encoding="utf-8") as f:
    exec(f.read(), globals())
