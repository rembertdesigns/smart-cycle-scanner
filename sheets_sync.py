import gspread
import pandas as pd
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials

# --- 🔐 Decode service_account.json from base64 for demo use ---
encoded_credentials = """PASTE_YOUR_BASE64_STRING_HERE"""
decoded = base64.b64decode(encoded_credentials).decode("utf-8")

with open("service_account.json", "w") as f:
    f.write(decoded)

# --- Setup ---
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "YOUR_GOOGLE_SHEET_ID_HERE"

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.sheet1

# --- Append a new log entry to Google Sheets ---
def append_cycle_log(data):
    worksheet = get_sheet()
    # Convert to native Python types to avoid serialization issues
    new_row = [
        str(data.get("timestamp")),
        str(data.get("sku")),
        str(data.get("item")),
        int(data.get("counted")),
        int(data.get("expected")),
        str(data.get("status"))
    ]
    worksheet.append_row(new_row)

# --- Load recent logs (optional for display in app) ---
def load_recent_logs():
    worksheet = get_sheet()
    records = worksheet.get_all_records()
    return pd.DataFrame(records)