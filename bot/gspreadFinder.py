from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
from recommendBot import Recommendation, OutputRestaurant

load_dotenv()


SERVICE_ACCOUNT_FILE = '../splendid-myth-353301-a63d721b9519.json'

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
RANGE_NAME = '시트1!A2:G30'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])

service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
values = result.get('values', [])

recommendation = Recommendation(values)
output_restaurant = OutputRestaurant

for rec_string in [OutputRestaurant(row.tolist()).__str__() for idx, row in recommendation.get_random(3).iterrows()]:
    print(rec_string)

print(recommendation.get_categorized_restaurant("한식"), 2)
print(recommendation.get_close_restaurant(0.2, 2))
