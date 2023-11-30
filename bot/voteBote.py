from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv


class VoteOutput:
    def __init__(self, vote_result):
        self.restaurant_name = vote_result[0]
        self.up_vote = vote_result[5]
        self.down_vote = vote_result[6]

    def __str__(self):
        return f"{self.restaurant_name}에 대한 추천 또는 비추가 완료되었습니다.\n"\
    + f"추천: {self.up_vote}\n"\
    + f"비추천: {self.down_vote}"


class VoteBote:

    def __init__(self, restaurant_name, restaurant_num=29):
        load_dotenv()

        self.restaurant_name = restaurant_name
        self.temp_row = []

        RANGE_NAME = f'시트1!A2:G{restaurant_num+1}'
        SERVICE_ACCOUNT_FILE = '../splendid-myth-353301-a63d721b9519.json'
        self.spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        self.service = build('sheets', 'v4', credentials=credentials)
        self.total_list = self.service \
            .spreadsheets().values() \
            .get(spreadsheetId=self.spreadsheet_id, range=RANGE_NAME).execute().get('values', [])
        self.get_restaurant_index()

    def get_restaurant_index(self):
        for i, row in enumerate(self.total_list):
            if row[0] == self.restaurant_name:
                self.temp_row = row
                return i + 2

        raise IndexError("해당 레스토랑이 리스트에 존재하지 않습니다.")

    def give_upvote(self):
        modified_values = [
            self.temp_row[:5] + [str(int(self.temp_row[5]) + 1)] + [self.temp_row[6]]
        ]

        update_values_request = {
            'values': modified_values
        }

        update_result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f'시트1!A{self.get_restaurant_index()}:G{self.get_restaurant_index()}',
            body=update_values_request,
            valueInputOption='RAW'  # Use 'RAW' if you're updating raw values
        ).execute()

        self.temp_row = modified_values[0]
        return str(VoteOutput(modified_values[0]))

    def give_downvote(self):
        modified_values = [
            self.temp_row[:6] + [str(int(self.temp_row[6]) + 1)]
        ]

        update_values_request = {
            'values': modified_values
        }

        update_result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f'시트1!A{self.get_restaurant_index()}:G{self.get_restaurant_index()}',
            body=update_values_request,
            valueInputOption='RAW'  # Use 'RAW' if you're updating raw values
        ).execute()

        self.temp_row = modified_values[0]
        return str(VoteOutput(modified_values[0]))


if __name__ == "__main__":
    vote_bote = VoteBote("솔향기")
    print(vote_bote.give_upvote())
    print(vote_bote.give_downvote())

