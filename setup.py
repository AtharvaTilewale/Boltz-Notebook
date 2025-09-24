# @title Install Dependencies and Boltz2 with CUDA support
import sys
import subprocess
import threading
import time
import os
import shutil
import datetime
import uuid
from zoneinfo import ZoneInfo
import getpass
import requests

# Google auth imports
from google.colab import auth
from googleapiclient.discovery import build

# ==== CONFIG ====
LOG_URL = "https://script.google.com/macros/s/AKfycbxPoo0REctEt-6eXRFg-ow3_iAueyOcG3y-XsIZ8PsSFTZWM5B_Y-IJyOoYQ9bf7Q03/exec"
NOTEBOOK_NAME = "Boltz2 v1.1"
SESSION_ID = str(uuid.uuid4())
JOB_TYPE = "installation"
JOB_NAME = "Boltz2 CUDA Setup"

os.chdir("/content/")

# ANSI color codes for colored output
class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

print(f"{Color.CYAN} ===Initialising Setup=== {Color.RESET}")
# ==== Google authentication and email retrieval ====
auth.authenticate_user()
service = build('oauth2', 'v2')
user_info = service.userinfo().get().execute()
USER_EMAIL = user_info.get('email', None)
USER_NAME = user_info.get('name', "unknown")  # <-- use Google account name

# ==== Logging function ====
def log_event(job_type=JOB_TYPE, job_name=JOB_NAME, event="visit"):
    now_ist = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    data = {
        "timestamp": now_ist.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "email": USER_EMAIL,
        "username": USER_NAME,  # real Google name
        "notebook": NOTEBOOK_NAME,
        "session_id": SESSION_ID,
        "job_type": job_type,
        "job_name": job_name,
        "event": event
    }
    try:
        requests.post(LOG_URL, data=data)
    except Exception as e:
        print(f"[{Color.RED}✘{Color.RESET}] Failed to log event: {e}")

log_event(job_type="Installation", job_name="Boltz Setup", event=" ")
# ==== Repos ====
repo_dirs = ["boltz"]

# ==== Steps ====
steps = [
    {
        "loader": f"{Color.CYAN}Cloning Boltz...{Color.RESET}",
        "done":   f"[{Color.GREEN}✔{Color.RESET}] Boltz cloned successfully.",
        "fail":   f"[{Color.RED}✘{Color.RESET}] boltz clone failed.",
        "cmd": ["git", "clone", "https://github.com/jwohlwend/boltz.git"]
    },
    {
        "loader": f"{Color.CYAN}Validating installation...{Color.RESET}",
        "done": f"[{Color.GREEN}✔{Color.RESET}] Validation complete.",
        "fail": f"[{Color.RED}✘{Color.RESET}] Validation failed.",
        "cmd": [sys.executable, "-c", "import torch; print('Torch CUDA available:', torch.cuda.is_available()); print('CUDA device count:', torch.cuda.device_count())"]
    }
]

# ==== Spinner loader ====
def loader(msg, stop_event):
    symbols = ["-", "\\", "|", "/"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r[{symbols[i % len(symbols)]}] {msg}   ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (len(msg) + 10) + "\r")

# ==== Remove existing repos ====
for repo in repo_dirs:
    if os.path.isdir(repo):
        print(f"{Color.YELLOW}[i] Repository already exists. Removing '{repo}'...{Color.RESET}")
        try:
            shutil.rmtree(repo)
            print(f"[{Color.GREEN}✔{Color.RESET}] Existing repository '{repo}' removed.")
        except Exception as e:
            print(f"[{Color.RED}✘{Color.RESET}] Failed to remove '{repo}': {e}")
            raise

all_success = True

# ==== Main steps ====
for step in steps:
    stop_event = threading.Event()
    t = threading.Thread(target=loader, args=(step["loader"], stop_event))
    t.start()
    try:
        subprocess.run(step["cmd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        stop_event.set()
        t.join()
        print(step["done"])
    except Exception as e:
        stop_event.set()
        t.join()
        print(f"{step['fail']} {e}")
        all_success = False
        break

# ==== Move Notebook dist folder ====
os.makedirs("/content/boltz_data", exist_ok=True)
try:
    shutil.move("/content/Boltz-Notebook/dist", "/content/boltz_data/")
    shutil.rmtree("/content/Boltz-Notebook")
except Exception as e:
    print(f"[{Color.RED}✘{Color.RESET}] Failed to move Notebook dist folder: {e}")

