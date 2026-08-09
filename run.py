import subprocess
import time
import sys


def start_api():
    print("🚀 Starting FastAPI server...")

    return subprocess.Popen(
        ["uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )


def wait_for_api():
    print("⏳ Waiting for API to be ready...")
    time.sleep(5)


def start_streamlit():
    print("🚀 Starting Streamlit app...")
    subprocess.run(["streamlit", "run", "frontend/app.py"])


if __name__ == "__main__":
    api_process = start_api()
    wait_for_api()

    try:
        start_streamlit()
    finally:
        print("🛑 Stopping API server...")
        api_process.terminate()