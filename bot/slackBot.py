from slack_sdk import WebClient
import os
from dotenv import load_dotenv

load_dotenv()

class SlackBot:
    def __init__(self, token):
        self.client = WebClient(token)
    
    def get_channel_id(self, channel_name):
        result = self.client.conversations_list()
        channels = result.data['channels']
        channel = list(filter(lambda c: c["name"] == channel_name, channels))[0]
        channel_id = channel["id"]
        return channel_id

    def get_message(self, channel_id, query):
        result = self.client.conversations_history(channel=channel_id)
        messages = result.data['messages']
        message = list(filter(lambda m: m['text'] == query, messages))[0]
        message_id = message["ts"]
        return message_id
    
    def post_message_in_thread(self, channel_id, message, text):
        result = self.client.chat_postMessage(
            channel=channel_id,
            thread_ts=message,
            text=text
        )
        return result
    
    def post_message(self, channel_id, text):
        result = self.client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        return result
    
    def post_qr_image(self, channel_id):
        result = self.client.chat_postMessage(
            channel=channel_id,
            text="출석체크 QR 이미지 입니다:",
            blocks=[
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": "출석체크 QR 이미지"
                    },
                    "image_url": "https://github.com/stoneHee99/kernel-slackbot/blob/main/src/image.png?raw=true",
                    "alt_text": "출석체크 QR 이미지"
                }
            ]
        )
        return result
