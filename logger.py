import requests, datetime, uuid

# ==== CONFIG ====
LOG_URL = "https://script.google.com/macros/s/AKfycbzbmG4_CJlFIlpQMqzPWkg9LqcH6XshSiBS7iGjaDOq-tjuPtoXEcRpYpupwEih3hcv/exec"   # <-- Replace with your Apps Script URL
NOTEBOOK_NAME = "Boltz2 v1.1"  # Change per notebook
SESSION_ID = str(uuid.uuid4())  # Unique ID for each runtime session

def log_event(event="visit"):
    """
    Log a minimal event to Google Sheets via Apps Script.
    Fields: timestamp, notebook, session_id, country, city, ip
    """
    # Base data
    data = {
        "timestamp": str(datetime.datetime.now()),
        "notebook": NOTEBOOK_NAME,
        "session_id": SESSION_ID,
    }

    # Send to Google Apps Script
    resp = requests.post(LOG_URL, data=data)