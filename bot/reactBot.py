import json
from flask import Flask, request, make_response
from slackBot import SlackBot
from recommendBot import OutputRestaurant, Recommendation
from voteBote import VoteBote
from gspreadFinder import get_spreadsheet_data
import os
from dotenv import load_dotenv
import re
import random

load_dotenv()

slack_token = os.getenv("SLACK_OAUTH_TOKEN")
myBot = SlackBot(slack_token)
app = Flask(__name__)

SERVICE_ACCOUNT_FILE = '../splendid-myth-353301-a63d721b9519.json'
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
RANGE_NAME = '시트1!A2:G30'


greetings = ["안녕", "하이", "방가"]

def show_how_to_use(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    text = "안녕하세요! 커널 360봇 입니다!\n멘션해주셔서 감사합니다.\n업데이트 및 관련 요청 문의는 석희님 원상님 현준님을 멘션해주세요."
    myBot.post_message(channel, text)
    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

def say_hello(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    text = "안녕하세요~! 반갑습니다 커널 봇입니다."
    myBot.post_message(channel, text)
    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

members = ["병룡님", "민협님", "영롱님", "원상님", "찬규님", "현지님", "찬욱님", "석희님", "민우님", "현준님", "예진님", "종민님", "소현님", "무룡님", "윤선님", "종찬님", "호윤님", "지용님", "형준님", "주광님"]

def randomMember(event_type, slack_event, num):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    num = int(num)
    selected_members = random.sample(members, min(num, len(members)))
    text = ', '.join(selected_members)
    myBot.post_message(channel, text)

    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

def randomMemberParameter(event_type, slack_event, num, arr):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    num = int(num)
    selected_members = random.sample(arr, min(num, len(arr)))
    text = ', '.join(selected_members)
    myBot.post_message(channel, text)

    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})
    
def randomRestaurant(event_type, slack_event, category, count):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    text = ""
    values = get_spreadsheet_data(SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, RANGE_NAME)
    recommendation = Recommendation(values)

    category_lower = category.lower()

    if "km" in category_lower:
        distance = float(category_lower.replace("km", ""))
    elif "m" in category_lower and "km" not in category_lower:
        distance = float(category_lower.replace("m", "")) / 1000

    if "km" in category_lower or ("m" in category_lower and "km" not in category_lower):
        for rec_string in [OutputRestaurant(row.tolist()).__str__() for idx, row in recommendation.get_close_restaurant(distance, int(count)).iterrows()]:
            text += rec_string + "\n"

    elif category_lower == "무작위":
        for rec_string in [OutputRestaurant(row.tolist()).__str__() for idx, row in recommendation.get_random(int(count)).iterrows()]:
            text += rec_string + "\n"

    else:
        for rec_string in [OutputRestaurant(row.tolist()).__str__() for idx, row in recommendation.get_categorized_restaurant(category, int(count)).iterrows()]:
            text += rec_string + "\n"

    if text:
        myBot.post_message(channel, text)
    else:
        message = "[%s] 적절한 카테고리를 찾을 수 없습니다." % category
        myBot.post_message(channel, message)

    return make_response(message, 200, {"X-Slack-No-Retry": 1})

def catch_restaurant(text):
    pattern = r"식당추천\s+(\S+)\s+(\d+)군데"
    match = re.search(pattern, text)

    if match:
        category = match.group(1)
        count = int(match.group(2))
        return category, count
    else:
        return

def sendQr(slack_event):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    myBot.post_qr_image(channel)
    return make_response(message, 200, {"X-Slack-No-Retry": 1})



def event_handler(event_type, slack_event):
    print(slack_event)
    if event_type == "app_mention":
        text = slack_event["event"]["text"]
        if "식당추천" in text:
            category, count = catch_restaurant(text)
            return randomRestaurant(event_type, slack_event, category, count)
        if re.search(r"추첨\s+\d+", text):
            num = re.search(r"추첨\s+(\d+)", text).group(1)

            is_array_parameter = re.search(r"\[(.*?)\]", text)
            if is_array_parameter:
                array_parameter = is_array_parameter.group(1).split(',')
                array_parameter = [parameter.strip() for parameter in array_parameter]
                return randomMemberParameter(event_type, slack_event, num, array_parameter)
            return randomMember(event_type, slack_event, num)

        if "qr" in text:
            return sendQr(slack_event)

        if "식당평가 추천" in text:
            channel = slack_event["event"]["channel"]
            if re.search(r"식당평가 추천\s+\w+", text):
                try:
                    message = VoteBote(re.search(r"식당평가 추천\s+(\w+)", text).group(1)).give_upvote()
                    myBot.post_message(channel, message)
                    return make_response(message, 200, {"X-Slack-No-Retry": 1})
                except IndexError as e:
                    e_message = e.__str__()
                    myBot.post_message(channel, e_message)
                    return make_response(e.__str__(), 200, {"X-Slack-No-Retry": 1})

        if "개추" in text:
            channel = slack_event["event"]["channel"]
            if re.search(r"개추\s+\w+", text):
                try:
                    message = VoteBote(re.search(r"개추\s+(\w+)", text).group(1)).give_upvote()
                    myBot.post_message(channel, message)
                    return make_response(message, 200, {"X-Slack-No-Retry": 1})
                except IndexError as e:
                    e_message = e.__str__()
                    myBot.post_message(channel, e_message)
                    return make_response(e.__str__(), 200, {"X-Slack-No-Retry": 1})

        if "비추" in text:
            channel = slack_event["event"]["channel"]
            if re.search(r"비추\s+\w+", text):
                try:
                    message = VoteBote(re.search(r"비추\s+(\w+)", text).group(1)).give_downvote()
                    myBot.post_message(channel, message)
                    return make_response(message, 200, {"X-Slack-No-Retry": 1})
                except IndexError as e:
                    e_message = e.__str__()
                    myBot.post_message(channel, e_message)
                    return make_response(e.__str__(), 200, {"X-Slack-No-Retry": 1})

        if "식당평가 비추" in text:
            channel = slack_event["event"]["channel"]
            if re.search(r"식당평가 비추\s+\w+", text):
                try:
                    message = VoteBote(re.search(r"식당평가 비추\s+(\w+)", text).group(1)).give_downvote()
                    myBot.post_message(channel, message)
                    return make_response(message, 200, {"X-Slack-No-Retry": 1})
                except IndexError as e:
                    e_message = e.__str__()
                    myBot.post_message(channel, e_message)
                    return make_response(e.__str__(), 200, {"X-Slack-No-Retry": 1})

        if any(greeting in text for greeting in greetings):
                return say_hello(event_type, slack_event) 
        return show_how_to_use(event_type, slack_event)

    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    test = "안녕하세요. 스레드 봇이 알 수 없는 요청입니다\n github에 issue report를 남겨주세요"
    myBot.post_message_in_thread(channel, message, test)

    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/slack", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        print (slack_event["challenge"])
        response_dict = {"challenge": slack_event["challenge"]}
        return response_dict
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return event_handler(event_type, slack_event)
    
    return make_response("슬랙 요청에 이벤트가 없습니다.", 404, {"X-Slack-No-Retry": 1})

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
