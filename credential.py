import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from account import *
import json
import re
from flask import Flask, request, make_response

app = Flask(__name__)

access_key, secret_key = access_key()
bot_token = slack_sdk_token()
account_list = account_list()

def aws_credential(account):
    # AWS credential을 입력합니다.
    if account == "cjcloud":
        session = boto3.Session(
            aws_access_key_id=access_key[0],
            aws_secret_access_key=secret_key[0],
            region_name='ap-northeast-2'
        )
        return session
    elif account == "cjonbill":
        session = boto3.Session(
            aws_access_key_id=access_key[1],
            aws_secret_access_key=secret_key[1],
            region_name='ap-northeast-2'
        )
        return session
    else:
        return session

# 원본 코드
# def aws_credential():
#     # AWS credential을 입력합니다.
#     session = boto3.Session(
#         aws_access_key_id=access_key[0],
#         aws_secret_access_key=secret_key[0],
#         region_name='ap-northeast-2'
#     )
#     return session

def slack_bot_token():
    client = WebClient(token=bot_token)
    return client

# 0 step
def select_account_quiry():
    client = slack_bot_token()
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "계정을 선택해주세요",
            blocks = select_account_quiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def select_account_quiry_block():
    block = [
        {
			"type": "image",
			"image_url": "https://img.cjnews.cj.net/wp-content/uploads/2020/10/ci_Bioetc._02.jpg",
			"alt_text": "image1",
		},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ">사용자 계정을 선택해주세요:"
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "사용자 계정을 선택해주세요",
                    "emoji": True
                },
                "options": [{
                    "text": {
                        "type": "plain_text",
                        "text": account
                    },
                    "value": account
                } for account in account_list]
            }
        }
    ]
    return block