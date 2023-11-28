from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()


SERVICE_ACCOUNT_FILE = 'splendid-myth-353301-a63d721b9519.json'

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
RANGE_NAME = '시트1!A2:G30'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])

service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])

if not values:
    print('데이터를 찾을 수 없습니다.')
else:
    for row in values:
        print(row)