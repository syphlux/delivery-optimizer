import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict

# Path to your JSON key
SERVICE_ACCOUNT_FILE = "app/credentials/credentials.json"

# Scopes define what the app can access
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Your sheet ID (from the URL)
SHEET_ID = "1QRdtVMtfJWh9QjqFE69xm6r5QJAuLDxl-J0rvHNchjo"

# Name of the worksheet/tab
WORKSHEET_NAME = "orders"


def get_google_sheet_data() -> List[Dict]:
    """Fetch all rows from Google Sheets and return as list of dicts."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    
    # Get all records (automatically uses first row as headers)
    records = worksheet.get_all_records()
    return records


if __name__ == "__main__":
    data = get_google_sheet_data()
    for row in data:
        print(row)
