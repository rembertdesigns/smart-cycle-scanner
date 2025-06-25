from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SHEET_ID = '15D6ZVuXf7W_0AYPSRq_8PeZaESZ9mEpgS4djmTRMDE0'

def append_cycle_log(data: dict):
    # Convert all data values to native Python types
    cleaned_data = {k: str(v) if isinstance(v, (int, float)) else v for k, v in data.items()}
    
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.sheet1

    new_row = [
        cleaned_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        cleaned_data.get("sku", ""),
        cleaned_data.get("item", ""),
        cleaned_data.get("location", ""),
        cleaned_data.get("counted", ""),
        cleaned_data.get("expected", ""),
        cleaned_data.get("variance", ""),
        cleaned_data.get("status", "")
    ]

    worksheet.append_row(new_row)