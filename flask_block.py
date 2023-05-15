from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from instance import *
from credential import *
from database import *
from elb import *
from s3service import *
from vpc import *
from mapplotlib import *
from detail_instance import *
from io import BytesIO
from PIL import Image
import time
import pytz

# Slack bot Token 받아오기
client = slack_bot_token()

def var_account():
    with open('data.txt', 'r') as f:
        account = f.read()
    return account

# 각 서비스에서 값 받아서 함수 생성
def var_instance(account):
    instance_count, instance_names, instance_ids, instance_types, instance_states, instance_public_ips, instance_os_types, instance_names_list, instance_states_list = ec2_count(account)
    return instance_count, instance_names, instance_ids, instance_types, instance_states, instance_public_ips, instance_os_types, instance_names_list, instance_states_list

def var_rds(account):
    rds_count, rds_identifier, rds_engine, rds_size, rds_status, rds_role = database_rds(account)
    return rds_count, rds_identifier, rds_engine, rds_size, rds_status, rds_role

def var_elb(account):
    elb_count, loadbalancer_name, loadbalancer_dns, loadbalancer_state, loadbalancer_type = elastic_loadbalancer(account)
    return elb_count, loadbalancer_name, loadbalancer_dns, loadbalancer_state, loadbalancer_type

def var_s3(account):
    s3_count, bucket_name, bucket_region, bucket_create_date = simple_storage_service(account)
    return s3_count, bucket_name, bucket_region, bucket_create_date

def var_vpc(account):
    vpc_count, vpc_name, vpc_state = vpc_counts(account)
    return vpc_count, vpc_name, vpc_state

def var_instance_ids_list(account):
    instance_ids_lists = instance_ids_list(account)
    return instance_ids_lists

def var_channel(account):
    channel_cj_vod, channel_cj_iptv, cpaas = detail_instance(account)
    return channel_cj_vod, channel_cj_iptv, cpaas

# 한국 표준시 설정
KST = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(tz=pytz.utc).astimezone(KST)
now_str = now.strftime('%Y-%m-%d %H:%M:%S')

# 1 step
def resource_quiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "어떤 작업을 수행하시겠습니까?",
            blocks = resource_list_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_list_inquiry_block():
    block = [
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *어떤 작업을 수행하시겠습니까? 현재 선택된 계정은 [" + var_account() + "] 입니다*"
			}
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "리소스 상태 조회"
                    },
                    "value": "click_me_123",
                    "action_id": "resource_status_inquiry",
                    "style": "danger"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "리소스 현황 조회"
                    },
                    "value": "click_me_123",
                    "action_id": "resource_current_inquiry",
                    "style": "primary"
                },
            ]
        },
    ]
    return block

# 2 step 리소스 상태 조회
def resource_status_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "리소스 상태 조회를 선택하셨습니다. 조회할 채널을 선택해주세요.",
            blocks = resource_status_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# 2 step 리소스 상태 조회 블록
def resource_status_inquiry_block():
    account = var_account()
    instance_count, instance_names, instance_ids, instance_types, instance_states, instance_public_ips, instance_os_types, instance_names_list, instance_states_list = var_instance(account)
    instance_ids_lists = var_instance_ids_list(account)
    
    block = [
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *리소스 상태 조회를 선택하셨습니다. 조회할 인스턴스를 선택해주세요.*"
			}
		},
        {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Name*"
				},
				{
					"type": "mrkdwn",
					"text": "*State*"
				},
            ],
		},
    ] + [
        {
            "type": "section",
            "fields": [
				{
					"type": "mrkdwn",
					"text": i
				},
				{
					"type": "mrkdwn",
					"text": j
				},
            ],
            "accessory": {
                "type": "overflow",
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "CPU Utilization",
                            "emoji": True
                        },
                        "value": f"cpu_{k}",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "MemoryUsage",
                            "emoji": True
                        },
                        "value": f"memory_{k}",
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "DiskUsage",
                            "emoji": True
                        },
                        "value": f"disk_{k}",
                    }
                ]
            }
        } for index, (i, j, k) in enumerate(zip(instance_names_list, instance_states_list, instance_ids_lists))
    ] + [
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 상태를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "resource_status_back",
                    "style": "danger"
			    },
            ]
        },
    ]
    return block

# 2 step 리소스 현황 조회
def resource_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "리소스 현황 조회를 선택하셨습니다. 조회할 채널을 선택해주세요.",
            blocks = resource_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# 2 step 리소스 현황 조회 블록
def resource_current_inquiry_block():
    block = [
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *리소스 현황 조회를 선택하셨습니다. 조회할 리소스를 선택해주세요.*"
			}
		},
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "value": "click_me_123",
                    "style": "danger",
                    "action_id": "resource_current_back"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "전체"
                    },
                    "value": "click_me_123",
                    "action_id": "total_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "EC2"
                    },
                    "value": "click_me_123",
                    "action_id": "ec2_instance"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "RDS"
                    },
                    "value": "click_me_123",
                    "action_id": "rds"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "ELB"
                    },
                    "value": "click_me_123",
                    "action_id": "elb"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "S3"
                    },
                    "value": "click_me_123",
                    "action_id": "s3_bucket"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "VPC"
                    },
                    "value": "click_me_123",
                    "action_id": "vpc"
                }
            ]
        }
    ]
    return block

# step 3 전체 리소스 현황 조회
def resource_total_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "전체를 선택하셨습니다.",
            blocks = resource_total_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# step 3 전체 리소스 현황 조회 블록
def resource_total_current_inquiry_block():
    account = var_account()
    instance_count, instance_names, instance_ids, instance_types, instance_states, instance_public_ips, instance_os_types, instance_names_list, instance_states_list = var_instance(account)
    rds_count, rds_identifier, rds_engine, rds_size, rds_status, rds_role = var_rds(account)
    elb_count, loadbalancer_name, loadbalancer_dns, loadbalancer_state, loadbalancer_type = var_elb(account)
    s3_count, bucket_name, bucket_region, bucket_create_date = var_s3(account)
    vpc_count, vpc_name, vpc_state = var_vpc(account)

    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *전체를 선택하셨습니다. 전체 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 인스턴스 수는 [" + str(instance_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ instance_names
                },
                {
                    "type": "mrkdwn",
                    "text": "*ID*\n" + instance_ids
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + instance_types
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + instance_states
                },
                {
                    "type": "mrkdwn",
                    "text": "*Public IP*\n" + instance_public_ips
                },
                # {
                #     "type": "mrkdwn",
                #     "text": "*OS*\n" + instance_os_types,
                # },
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 RDS 수는 [" + str(rds_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ rds_identifier
                },
                {
                    "type": "mrkdwn",
                    "text": "*Role*\n" + rds_role
                },
                {
                    "type": "mrkdwn",
                    "text": "*Engine*\n" + rds_engine
                },
                {
                    "type": "mrkdwn",
                    "text": "*Size*\n" + rds_size
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + rds_status
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 ELB 수는 [" + str(elb_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ loadbalancer_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*DNS name*\n" + loadbalancer_dns
                },
                {
                    "type": "mrkdwn",
                    "text": "*State*\n" + loadbalancer_state
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + loadbalancer_type
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 S3 수는 [" + str(s3_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ bucket_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*Region*\n" + bucket_region
                },
                {
                    "type": "mrkdwn",
                    "text": "*Create date*\n" + bucket_create_date
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 VPC 수는 [" + str(vpc_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*VPC ID*\n"+ vpc_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*State*\n" + vpc_state
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "value": "click_me_123",
                    "style": "danger",
                    "action_id": "resource_current_total_back"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 3 EC2 리소스 현황 조회
def resource_ec2_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "EC2를 선택하셨습니다.",
            blocks = resource_ec2_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_ec2_current_inquiry_block():
    account = var_account()
    instance_count, instance_names, instance_ids, instance_types, instance_states, instance_public_ips, instance_os_types, instance_names_list, instance_states_list = var_instance(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *EC2를 선택하셨습니다. EC2 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 인스턴스 수는 [" + str(instance_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ instance_names
                },
                {
                    "type": "mrkdwn",
                    "text": "*ID*\n" + instance_ids
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + instance_types
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + instance_states
                },
                {
                    "type": "mrkdwn",
                    "text": "*Public IP*\n" + instance_public_ips
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "resource_current_ec2_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block


# step 3 RDS 리소스 현황 조회
def resource_rds_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "RDS를 선택하셨습니다.",
            blocks = resource_rds_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_rds_current_inquiry_block():
    account = var_account()
    rds_count, rds_identifier, rds_engine, rds_size, rds_status, rds_role = var_rds(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *RDS를 선택하셨습니다. RDS 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 RDS 수는 [" + str(rds_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ rds_identifier
                },
                {
                    "type": "mrkdwn",
                    "text": "*Role*\n" + rds_role
                },
                {
                    "type": "mrkdwn",
                    "text": "*Engine*\n" + rds_engine
                },
                {
                    "type": "mrkdwn",
                    "text": "*Size*\n" + rds_size
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + rds_status
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "resource_current_rds_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 3 ELB 리소스 현황 조회
def resource_elb_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "ELB를 선택하셨습니다.",
            blocks = resource_elb_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_elb_current_inquiry_block():
    account = var_account()
    elb_count, loadbalancer_name, loadbalancer_dns, loadbalancer_state, loadbalancer_type = var_elb(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *ELB를 선택하셨습니다. ELB 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 ELB 수는 [" + str(elb_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ loadbalancer_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*DNS name*\n" + loadbalancer_dns
                },
                {
                    "type": "mrkdwn",
                    "text": "*State*\n" + loadbalancer_state
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + loadbalancer_type
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "resource_current_elb_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 3 S3 리소스 현황 조회
def resource_s3_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "S3를 선택하셨습니다.",
            blocks = resource_s3_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# step 3 S3 리소스 현황 조회 블록
def resource_s3_current_inquiry_block():
    account = var_account()
    s3_count, bucket_name, bucket_region, bucket_create_date = var_s3(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *S3를 선택하셨습니다. S3 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 S3 수는 [" + str(s3_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n"+ bucket_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*Region*\n" + bucket_region
                },
                {
                    "type": "mrkdwn",
                    "text": "*Create date*\n" + bucket_create_date
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "value": "click_me_123",
                    "action_id": "resource_current_s3_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "value": "click_me_123",
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 3 VPC 리소스 현황 조회
def resource_vpc_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "VPC를 선택하셨습니다.",
            blocks = resource_vpc_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# step 3 S3 리소스 현황 조회 블록
def resource_vpc_current_inquiry_block():
    account = var_account()
    vpc_count, vpc_name, vpc_state = var_vpc(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ">:mag: *VPC를 선택하셨습니다. VPC 리소스에 대한 정보입니다.*"
			},
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 VPC 수는 [" + str(vpc_count) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*VPC ID*\n"+ vpc_name
                },
                {
                    "type": "mrkdwn",
                    "text": "*State*\n" + vpc_state
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "value": "click_me_123",
                    "action_id": "resource_current_vpc_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "value": "click_me_123",
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 4 채널CJ-VOD 리소스 현황 조회
def resource_channel_cj_vod_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "채널CJ-VOD를 선택하셨습니다.",
            blocks = resource_channel_cj_vod_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_channel_cj_vod_current_inquiry_block():
    account = var_account()
    channel_cj_vod, channel_cj_iptv, cpaas = var_channel(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *채널CJ-VOD를 선택하셨습니다. 채널CJ-VOD에 대한 정보입니다.*"
			}
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 인스턴스 수는 [" + str(channel_cj_vod[0]) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n" + channel_cj_vod[1]
                },
                {
                    "type": "mrkdwn",
                    "text": "*ID*\n" + channel_cj_vod[2]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + channel_cj_vod[3]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + channel_cj_vod[4]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Public IP*\n" + channel_cj_vod[5]
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "channel_cj_vod_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "value": "click_me_123",
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 4 채널CJ-IPTV 리소스 현황 조회
def resource_channel_cj_iptv_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "채널CJ-IPTV를 선택하셨습니다.",
            blocks = resource_channel_cj_iptv_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_channel_cj_iptv_current_inquiry_block():
    account = var_account()
    channel_cj_vod, channel_cj_iptv, cpaas = var_channel(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *채널CJ-IPTV를 선택하셨습니다. 채널CJ-IPTV에 대한 정보입니다.*"
			}
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 인스턴스 수는 [" + str(channel_cj_iptv[0]) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n" + channel_cj_iptv[1]
                },
                {
                    "type": "mrkdwn",
                    "text": "*ID*\n" + channel_cj_iptv[2]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + channel_cj_iptv[3]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + channel_cj_iptv[4]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Public IP*\n" + channel_cj_iptv[5]
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "channel_cj_iptv_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 4 CPAAS 리소스 현황 조회
def resource_cpaas_current_inquiry():
    try:
        response = client.chat_postMessage(
            channel = "#chatbot_test",
            text = "CPAAS를 선택하셨습니다.",
            blocks = resource_cpaas_current_inquiry_block(),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_cpaas_current_inquiry_block():
    account = var_account()
    channel_cj_vod, channel_cj_iptv, cpaas = var_channel(account)
    block = [
        {
			"type": "image",
			"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyyG-FSWPWbi2uXldqYz2li4Ctu7hpexAmqbGIVq6TLW04sU6wXywBeufnl7FCwA3XA&usqp=CAU",
			"alt_text": "image1",
		},
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": ":mag: *CPAAS를 선택하셨습니다. CPAAS에 대한 정보입니다.*"
			}
		},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "현재 AWS 상에서 조회된 인스턴스 수는 [" + str(cpaas[0]) + "]개 입니다."
                },
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Name*\n" + cpaas[1]
                },
                {
                    "type": "mrkdwn",
                    "text": "*ID*\n" + cpaas[2]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Type*\n" + cpaas[3]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Status*\n" + cpaas[4]
                },
                {
                    "type": "mrkdwn",
                    "text": "*Public IP*\n" + cpaas[5]
                },
            ]
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*채널에 해당하는 AWS 리소스 현재 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "cpaas_back",
                    "style": "danger"
			    },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-VOD"
                    },
                    "action_id": "channel_cj_vod_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "채널CJ-IPTV"
                    },
                    "action_id": "channel_cj_iptv_current"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CPAAS"
                    },
                    "action_id": "cpaas_current"
                }
            ]
        }
    ]
    return block

# step 4 cloudwatch image
# def resource_cloudwatch_image_inquiry():
#     images = [get_cloudwatch_cpu_image(), get_cloudwatch_memory_image()]
#     for image in images:
#         try:
#             response = client.files_upload_v2(
#                 channel="C04SPF4LP4P",
#                 file=image,
#                 filename='graph.png',
#                 initial_comment='>AWS CloudWatch 그래프 이미지',
#             )
#             print(f"Successfully sent the message: {response['ts']}")
#         except SlackApiError as e:
#             print("Error sending message: {}".format(e))
#             print(e.response)

# def resource_cloudwatch_image_inquiry():
#     # Combine the two images horizontally
#     images = [Image.open(BytesIO(get_cloudwatch_cpu_image())), Image.open(BytesIO(get_cloudwatch_memory_image())), Image.open(BytesIO(get_cloudwatch_memory_image())), Image.open(BytesIO(get_cloudwatch_memory_image()))]
#     widths, heights = zip(*(i.size for i in images))
#     total_width = sum(widths)
#     max_height = max(heights)
#     new_im = Image.new('RGB', (total_width, max_height))
#     x_offset = 0
#     for im in images:
#         new_im.paste(im, (x_offset, 0))
#         x_offset += im.size[0]

#     # Upload the combined image to Slack
#     try:
#         with BytesIO() as output:
#             new_im.save(output, format='PNG')
#             contents = output.getvalue()
#         response = client.files_upload_v2(
#             channel="C04SPF4LP4P",
#             file=contents,
#             filename='graphs.png',
#             initial_comment='>AWS CloudWatch 그래프 이미지',
#         )
#     except SlackApiError as e:
#         print("Error sending message: {}".format(e))
#         print(e.response)

# 이미지 타이틀 내용
def resource_cloudwatch_image_content_head_block(instance_id):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f">>>다음은 {instance_id} 인스턴스에 대한 모니터링 결과입니다."
            }
        },
    ]
    return blocks

# 이미지 텍스트 내용
def resource_cloudwatch_image_content_block(instance_id, system_info):
    url = cloudwatch_url(instance_id)
    blocks = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Metric:*\n" + system_info
                },
                {
                    "type": "mrkdwn",
                    "text": "*When:*\n" + now_str
                },
                {
                    "type": "mrkdwn",
                    "text": "*Previous State:*\n정상"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Current State:*\n정상"
                },
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*CloudWatch monitoring URL:* \n```<{url}>```"
            }
        },
        {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
					"alt_text": "notifications warning icon"
				},
				{
					"type": "mrkdwn",
					"text": "*모니터링된 AWS 리소스 상태 현황를 조회합니다.*"
				}
			]
		},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Back"
				    },
                    "action_id": "cloudwatch_monitoring_back",
                    "style": "danger"
			    },
            ]
        }
    ]
    return blocks


def resource_cloudwatch_image_content_head_inquiry(instance_id):
    try:
        response = client.chat_postMessage(
            channel='#chatbot_test',
            text='asd',
            blocks=resource_cloudwatch_image_content_head_block(instance_id),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

def resource_cloudwatch_image_content_inquiry(instance_id, system_info):
    try:
        resource_cloudwatch_image_content_head_inquiry(instance_id),
        if system_info == "CPU Utilization":
            resource_cloudwatch_cpu_image_inquiry(instance_id)
        elif system_info == "Memory Used Percent":
            resource_cloudwatch_memory_image_inquiry(instance_id)
        elif system_info == "Disk Used Percent":
            resource_cloudwatch_disk_image_inquiry(instance_id)
        time.sleep(2)
        response = client.chat_postMessage(
            channel='#chatbot_test',
            text='asd',
            blocks=resource_cloudwatch_image_content_block(instance_id, system_info),
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))

# step 4 cloudwatch CPU image
def resource_cloudwatch_cpu_image_inquiry(instance_id):
    account = var_account()
    images = [matplotlib_cpu_image(instance_id, account)]
    for image in images:
        try:
            response = client.files_upload_v2(
                channel="C053R0VNU2Y", #C04SPF4LP4P
                file=image,
                filename='graph.png',
            )
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            print(e.response)

# step 4 cloudwatch Memory image
def resource_cloudwatch_memory_image_inquiry(instance_id):
    account = var_account()
    images = [matplotlib_memory_image(instance_id, account)]
    for image in images:
        try:
            response = client.files_upload_v2(
                channel="C053R0VNU2Y", #C04SPF4LP4P
                file=image,
                filename='graph.png',
            )
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            print(e.response)

# step 4 cloudwatch Disk image
def resource_cloudwatch_disk_image_inquiry(instance_id):
    account = var_account()
    images = [matplotlib_disk_image(instance_id, account)]
    for image in images:
        try:
            response = client.files_upload_v2(
                channel="C053R0VNU2Y", #C04SPF4LP4P
                file=image,
                filename='graph.png',
            )
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            print(e.response)