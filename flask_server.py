import json
import re
from datetime import datetime
from flask import Flask, request, make_response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask_block import *
from instance import *
from query import *
from credential import *

app = Flask(__name__)
client = slack_bot_token()

account = var_account()

# instance count
instance_count = instance_count_len(account)

def instance_info(account):
    instance_ids_list = instance_ids_list(account)
    return instance_ids_list

# 캐시 관련 헤더를 제거하는 함수
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# after_request 데코레이터를 사용하여 모든 응답에 대해 캐시 관련 헤더를 제거
@app.after_request
def apply_caching(response):
    return after_request(response)

@app.route('/', methods=['POST'])
def event_handler():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    event = slack_event["event"]
    if event["type"] == "app_mention":
        query = event['blocks'][0]['elements'][0]['elements'][1]['text'].replace(" ", "")
        query = query.lower()
        # AWS 서비스
        service_queries = {
            "전체": resource_total_current_inquiry,
            "ec2": resource_ec2_current_inquiry,
            "rds": resource_rds_current_inquiry,
            "elb": resource_elb_current_inquiry,
            "s3": resource_s3_current_inquiry,
        }
        if query in service_queries:
            service_queries[query]()
        elif query == "조회":
            resource_quiry()
        elif query == "계정":
            select_account_quiry()
        elif query == "리소스상태조회":
            resource_status_inquiry()
        elif query == "리소스현황조회":
            resource_current_inquiry()
        elif query == "전체":
            resource_total_current_inquiry()
        elif query == "ec2":
            resource_ec2_current_inquiry()
        elif query == "rds":
            resource_rds_current_inquiry()
        elif query == "elb":
            resource_elb_current_inquiry()
        elif query == "s3":
            resource_s3_current_inquiry()
        elif query == "vpc":
            resource_vpc_current_inquiry()
        else:
            response = get_answer(query)
            client.chat_postMessage(channel=event["channel"], text=response)
            return make_response("ok", 200)
    return make_response("ok", 200)

@app.route("/slack/message_actions", methods=["POST"])
def handle_account_select():
    payload = json.loads(request.form.get("payload"))

    # step 2 리소스 상태 조회하기
    if payload["actions"][0]["action_id"] == "resource_status_inquiry":
        resource_status_inquiry()
    # step 2 리소스 상태 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_status_back":
        resource_quiry()
    # step 2 리소스 현황 조회하기
    elif payload["actions"][0]["action_id"] == "resource_current_inquiry":
        resource_current_inquiry()
    # step 2 리소스 현황 조회 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_back":
        resource_quiry()
    # step 3 전체 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "total_current":
        resource_total_current_inquiry()
    # step 3 전체 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_total_back":
        resource_current_inquiry()
    # step 3 EC2 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "ec2_instance":
        resource_ec2_current_inquiry()
    # step 3 EC2 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_ec2_back":
        resource_current_inquiry()
    # step 3 RDS 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "rds":
        resource_rds_current_inquiry()
    # step 3 RDS 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_rds_back":
        resource_current_inquiry()
    # step 3 ELB 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "elb":
        resource_elb_current_inquiry()
    # step 3 ELB 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_elb_back":
        resource_current_inquiry()
    # step 3 S3 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "s3_bucket":
        resource_s3_current_inquiry()
    # step 3 S3 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_s3_back":
        resource_current_inquiry()
    # step 3 VPC 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "vpc":
        resource_vpc_current_inquiry()
    # step 3 VPC 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "resource_current_vpc_back":
        resource_current_inquiry()
    # step 4 채널 CJ VOD 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "channel_cj_vod_current":
        resource_channel_cj_vod_current_inquiry()
    # step 4 채널 CJ VOD 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "channel_cj_vod_back":
        resource_total_current_inquiry()
    # step 4 채널 CJ IPTV 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "channel_cj_iptv_current":
        resource_channel_cj_iptv_current_inquiry()
    # step 4 채널 CJ IPTV 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "channel_cj_iptv_back":
        resource_total_current_inquiry()
    # step 4 채널 CPAAS 리소스 현황 보기
    elif payload["actions"][0]["action_id"] == "cpaas_current":
        resource_cpaas_current_inquiry()
    # step 4 채널 CPAAS 리소스 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "cpaas_back":
        resource_total_current_inquiry()

    # 그래프 임시
    elif payload["actions"][0]["action_id"] == "graph":
        resource_cloudwatch_image_content_inquiry()
    
    # step 4 CloudWatch Image 가져오기
    elif payload["actions"][0]["action_id"] == "cloudwatch_image":
        resource_cloudwatch_image_inquiry()

    # step 4 cloudwatch 리소스 상태 현황 뒤로가기
    elif payload["actions"][0]["action_id"] == "cloudwatch_monitoring_back":
        resource_status_inquiry_block()

    elif payload['actions'][0]['selected_option']['value'] == "cjcloud":
        with open('data.txt', 'w') as f:
            f.write("cjcloud")
        resource_quiry()

    elif payload['actions'][0]['selected_option']['value'] == "cjonbill":
        with open('data.txt', 'w') as f:
            f.write("cjonbill")
        resource_quiry()

    account = var_account()

    # step 2 리소스 상태 조회 CPU
    for instance_id in instance_ids_list(account):
        if payload['actions'][0]['selected_option']['value'] == f"cpu_{instance_id}":
            resource_cloudwatch_image_content_inquiry(instance_id, "CPU Utilization")
        elif payload['actions'][0]['selected_option']['value'] == f"memory_{instance_id}":
            resource_cloudwatch_image_content_inquiry(instance_id, "Memory Used Percent")
        elif payload['actions'][0]['selected_option']['value'] == f"disk_{instance_id}":
            resource_cloudwatch_image_content_inquiry(instance_id, "Disk Used Percent")
        else:
            pass
    return make_response("ok", 200)

def get_answer(query):
    aws_query_list = aws_query()
    answers = {
        '헬프': "도와줄 수 있는 명령어는 리소스 상태 조회, 리소스 현황 조회, 리소스 수정 등이 있습니다.",
        'help': "도와줄 수 있는 명령어는 리소스 상태 조회, 리소스 현황 조회, 리소스 수정 등이 있습니다.",
        '명령어': aws_query_list
    }

    query = query.lower()

    for key in answers.keys():
        if key in query:
            return answers[key]

    for key in answers.keys():
        if query in key:
            return "연관 단어 [" + key + "]에 대한 답변입니다.\n" + answers[key]

    return "알 수 없는 질의입니다. 답변을 드릴 수 없습니다."

if __name__ == '__main__':
    app.run(debug=True, port=5002)