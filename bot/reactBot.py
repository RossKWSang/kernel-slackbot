import json
from flask import Flask, request, make_response
from slackBot import SlackBot
import os
from dotenv import load_dotenv

load_dotenv()

slack_token = os.getenv("SLACK_OAUTH_TOKEN")
myBot = SlackBot(slack_token)
app = Flask(__name__)

def show_how_to_use(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    message = slack_event["event"]["event_ts"]
    text = "안녕하세요! 커널 360봇 입니다!\n멘션해주셔서 감사합니다.\n업데이트 및 관련 요청 문의는 석희님 원상님 현준님을 멘션해주세요."
    myBot.post_message(channel, message, text)
    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


def event_handler(event_type, slack_event):
    print(slack_event)

    if(event_type == "app_mention"): return show_how_to_use(event_type, slack_event);

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
