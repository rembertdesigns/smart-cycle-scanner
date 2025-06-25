import gspread
import pandas as pd
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials

# --- 🔐 Decode credentials from embedded base64 string ---
encoded_credentials = """ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic21hcnQtY3ljbGUtc2Nhbm5lci1kZW1vIiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiNzQ1OWNhMjY4YWM4YzM0MmQ4M2MzMWY5YTRlMzQzNGI3M2QzYjIxMyIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZnSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2d3Z2dTa0FnRUFBb0lCQVFEQlZRdnZ5REhFbkdHOVxuU1VCMWRsT1NHSTBNUHNXdnUyd25Ld2hBK0hNU1BsdXYzM21CSDg2MHlKZHVoYjdqd3lYZHBtYzRKa0UwQWRaT1xuUzd2Tnk0UGZDblpzMk83TEpKc09zd0UzRFI1UXJobmVlTURmZFlSTktuT0FTQVhobjg5M3BYME1ZRUFoQU5FVlxuaW85RDNVYzhNREdDbTlIU0xHSndUK1lNYTB6ZktlaG9MajNyeWtaNzBtOEJBTndKeFRwcEQ1cm9CVDFFTXV6clxuV0FwNHBxWmVLWERSQzY3eWkxa0RHZHI0c2RNKzZtZ3QyUVVCRHZhNGsxTElsdUplcnFMU2d5M01HWkgzSWszMFxuWXNEVkZOVERkdXhiSVZ2ZEtRZ0xRbC8xY3J3WE9zWTB6eGVuc1Q0dVdTRi9lazh6NHQwZTFtL3dhK2hQbXZzOFxuVUNSdGxZRTVBZ01CQUFFQ2dnRUFGaDYzVU1vbW9wU1RiTU05c2lyVmpUN01uWkR0a0ttWXFtTVdyTXRZYkNjUlxuR2I1dmtoM3I2anlVc2U4d3kvRzdLb0QwYUtUYzJ6aldGcXQ4MjRNY2JaZXVmTTMxeFcyazVaSEcwdkFIN3NwNlxudUh6M3NXR0tYNE5heDN2R0czNXIwQWhSMWttSmNOVTlkdkhkYWpIK1NXVkl0dVZCNUtLU0tVQkZCWmo5eUw4WlxuZVBybS9TYlh0Z1A2dE5MdWthaDZPMmNaUGtsZHkvbzJsRitsZ3lvSldNeC9tUFZLK3h1SVU1Uk9hWW1uVkJyUVxuQVh6L002OERjblo5RFRaMDdVTlNzbXBrS2YzS25FVFpZRzFiVW5iQTZRY0ZiNmFJMjJab1prS0E3WXZVVDA3Y1xuaEkrUVZkaVhxSVNSS2FhWXVRUU55SGd4OTA3VzVPeHRITVFRZkZGYU1RS0JnUURmTlJLcE9lTUw3WHNrUlZZa1xuMXVhRGY2a1ZsanhJcGo1YVIzdFh6eGdRM1hCc3BvZWVLOFZUcHhXcmFmK3l4MW45ZlZjdHBYZUQrQzVnemlSaFxuNy9wajd0RFArUHB0cHRJM2pRZDFqb1RRR0tsYXRBbmpCQU9rVFJFdWdQQ0dtK2c5WkNEcjJlaThsWHEzNm1hMVxuWXZWZWFtNExseUk1R1FLRUhvR2tyZzFuYVFLQmdRRGR2RnVWUFVWOTRMcVhXT29TV056ZHVheFp4TEx0ZW5oUlxuNkFNWDBibmtJVm9DcTIwdU5xT3gxcjlzSDhaTHR1dVUzM1dLTVkyQUUyV2JNS0h4cWx4YUNrMTVRYXFsVy82ZlxuYlRtaG5YbEgwUktsT3hhbkJZTHN6S2lJdzVtQ3QxY1pJWFJja1lPMlo2SnFyemxKdWdianc4YXZ4aW84K1VKa1xuR2g0ZnFjRmhVUUtCZ1FEVWwyUVNzZ1BDVklvNDNhRlNyU3dZaXZxc2lNOGFFdHpJZDlUT3FYeXVjM3Frd1dmaVxuQ3FhREtsekZTc3d6cHhQYkVBcDhlMkQ5M04rdmJDZlM4Qko0SS9uV1c3bUp2cDN5TXV5cjF2WkFqWHlmMjJLZlxuU2k5OXlibFhwWTl4WmdVb2s3bVhhWkQyTFJrWkdyU0FocVJWTE9GclFLTmo1cUl5M0N0MmdpQmFJUUtCZ1FER1xuR1gwYzVTUExwVll1MXpJd2VCSERTaG53RFdycC9ldTNDWGlSOUQ2RzBVRXdkMlZRejJJS0JWajV5WjJJa1lFQlxuZlc3dXF2ekhPdzBnekI4eTRFZ243V0p2L2JudWlEVUF6RDJiNVN1d2ZOcVNvaXJIeDRYRDk4aHVmNG9MbmE4RFxuOWI2VzRTNXliVDVPNEFObm1mcUR6S29hNmdsY2RqalpZL2didzdiUU1RS0JnRjgzdnByRENLdWdyb0doMkpTWVxuNzRWNzFwa2JUdVR6SGZLZExacXFMU1FVVFlNWUdpWXdtRDM4d2p3Zm5PTkt0MzdSTEI4Z1pIcUZJZ0RIRTIwWVxuQUlxOEViR1FkYWRQd1NyR0FwNXU2K0VveEVSNEhDamhsdUZodzQyU2dUSWFySW1kV2ZLZmV6cThCQk5MVVh2UlxuempPYld6YkErdWdMTlhZb0tjMmtxa1dNXG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4="""

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

# --- Append log entry to Google Sheets ---
def append_cycle_log(data):
    worksheet = get_sheet()
    new_row = [
        str(data.get("timestamp")),
        str(data.get("sku")),
        str(data.get("item")),
        int(data.get("counted")),
        int(data.get("expected")),
        str(data.get("status"))
    ]
    worksheet.append_row(new_row)

# --- (Optional) Load recent scan logs ---
def load_recent_logs():
    worksheet = get_sheet()
    records = worksheet.get_all_records()
    return pd.DataFrame(records)