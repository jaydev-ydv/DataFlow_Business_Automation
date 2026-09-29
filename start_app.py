"""
Startup script to run both Frontend (Streamlit) and Backend (Flask) services.
Run this script to start the complete business automation application.

Usage:
    python start_app.py          # Start both services
    python start_app.py backend  # Start only backend
    python start_app.py frontend # Start only frontend
"""

import os
import sys
import subprocess
import time
import signal


def is_port_in_use(port):
    """Check if a port is already in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def start_backend():
    """Start the Flask backend server."""
    backend_dir = os.path.join(os.path.dirname(__file__), "Backend(Flask ApI)")
    app_path = os.path.join(backend_dir, "app.py")
    backend_env = {**os.environ, "FLASK_ENV": "development", "FLASK_APP": "app"}
    
    print("=" * 50)
    print("Starting Backend (Flask API) on http://127.0.0.1:5000")
    print("=" * 50)
    
    # Check if port is already in use
    if is_port_in_use(5000):
        print("Warning: Port 5000 is already in use. Backend may already be running.")
        return None
    
    # Set working directory to backend
    original_dir = os.getcwd()
    os.chdir(backend_dir)
    
    try:
        print("Applying database migrations...")
        subprocess.run(
            [sys.executable, "-m", "flask", "db", "upgrade"],
            cwd=backend_dir,
            env=backend_env,
            check=True,
        )

        proc = subprocess.Popen(
            [sys.executable, app_path],
            env=backend_env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        return proc
    finally:
        os.chdir(original_dir)


def start_frontend():
    """Start the Streamlit frontend server."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "Frontend(Streamlit UI)")
    app_path = os.path.join(frontend_dir, "app.py")
    
    print("=" * 50)
    print("Starting Frontend (Streamlit UI) on http://127.0.0.1:8501")
    print("=" * 50)
    
    # Check if port is already in use
    if is_port_in_use(8501):
        print("Warning: Port 8501 is already in use. Frontend may already be running.")
        return None
    
    # Set working directory to frontend
    original_dir = os.getcwd()
    os.chdir(frontend_dir)
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", app_path, 
             "--server.port", "8501", "--server.address", "127.0.0.1"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        return proc
    finally:
        os.chdir(original_dir)


def main(): 
    """Main entry point."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    backend_process = None
    frontend_process = None
    
    def signal_handler(sig, frame):
        """Handle Ctrl+C to terminate all processes."""
        print("\nShutting down services...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    if not args or "backend" in args:
        backend_process = start_backend()
        time.sleep(2)  # Give backend time to start
    
    if not args or "frontend" in args:
        frontend_process = start_frontend()
    
    if backend_process or frontend_process:
        print("\n" + "=" * 50)
        print("Application is running!")
        print("  - Backend API: http://127.0.0.1:5000")
        print("  - Frontend UI:  http://127.0.0.1:8501")
        print("  - API Health:  http://127.0.0.1:5000/health")
        print("=" * 50)
        print("\nPress Ctrl+C to stop all services.")
        
        try:
            if backend_process:
                backend_process.wait()
            if frontend_process:
                frontend_process.wait()
        except KeyboardInterrupt:
            signal_handler(None, None)
    else:
        print("No services started. Check if ports 5000 or 8501 are already in use.")


if __name__ == "__main__":
    main()
