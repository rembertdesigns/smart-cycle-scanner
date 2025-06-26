import gspread
import pandas as pd
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from logic import compute_severity

# --- 🔐 Decode credentials from embedded base64 string ---
encoded_credentials = "..."  # your long base64 key
decoded = base64.b64decode(encoded_credentials.strip()).decode("utf-8")

# Write the decoded credentials to a temporary file
with open("service_account.json", "w") as f:
    f.write(decoded)

# --- Setup Google Sheets connection ---
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "15D6ZVuXf7W_0AYPSRq_8PeZaESZ9mEpgS4djmTRMDE0"

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.sheet1

# --- ⭐ Calculate severity score ---
def calculate_severity(discrepancy, category):
    if abs(discrepancy) > 5:
        return 5
    elif category and category.lower() in ["vape", "extracts", "concentrates", "edibles"]:
        return 4 if abs(discrepancy) > 0 else 1
    elif abs(discrepancy) > 2:
        return 3
    elif abs(discrepancy) > 0:
        return 2
    return 1

# --- Append log entry to Google Sheets ---
def append_cycle_log(data):
    worksheet = get_sheet()
    discrepancy = data.get("counted", 0) - data.get("expected", 0)
    severity = calculate_severity(discrepancy, data.get("category", ""))
    new_row = [
        str(data.get("timestamp")),
        str(data.get("sku")),
        str(data.get("item")),
        int(data.get("counted")),
        int(data.get("expected")),
        discrepancy,
        str(data.get("status")),
        severity
    ]
    worksheet.append_row(new_row)

# --- (Optional) Load recent scan logs ---
def load_recent_logs():
    worksheet = get_sheet()
    records = worksheet.get_all_records()
    return pd.DataFrame(records)