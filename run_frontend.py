import os
import subprocess
import sys

port = os.getenv("PORT", "8501")
cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "Frontend(Streamlit UI)/app.py",
    "--server.port",
    str(port),
    "--server.address",
    "0.0.0.0",
    "--server.enableCORS",
    "false",
    "--server.enableXsrfProtection",
    "false",
    "--server.headless",
    "true",
]

print(f"Starting Streamlit on port {port}...")
sys.exit(subprocess.call(cmd))
