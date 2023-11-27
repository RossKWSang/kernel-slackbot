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

slack_token = os.getenv("SLACK_OAUTH_TOKEN")
myBot = SlackBot(slack_token);

channel_id = myBot.get_channel_id("slackbot-test");
message = myBot.get_message(channel_id, '하이')
result = myBot.post_message_in_thread(channel_id, message, "안녕하세요")

print(result);