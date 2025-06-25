import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Path to your downloaded JSON key
SERVICE_ACCOUNT_FILE = "service_account.json"

# Your Google Sheet ID
SHEET_ID = "https://docs.google.com/spreadsheets/d/15D6ZVuXf7W_0AYPSRq_8PeZaESZ9mEpgS4djmTRMDE0/edit?gid=0#gid=0"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def append_cycle_log(row_data):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.sheet1

    timestamp = datetime.now().isoformat()
    row = [timestamp] + row_data
    worksheet.append_row(row)

    return True
