import os
import boto3
from credential import *

def detail_instance(account):
    session = aws_credential(account)

    # EC2 client 생성
    ec2_client = session.client('ec2')

    response = ec2_client.describe_instances()

    # 인스턴스 리스트 생성
    channel_cj_vod_names_list = []
    channel_cj_vod_ids_list = []
    channel_cj_vod_type_list = []
    channel_cj_vod_status_list = []
    channel_cj_vod_public_ips_list = []

    channel_cj_iptv_names_list = []
    channel_cj_iptv_ids_list = []
    channel_cj_iptv_type_list = []
    channel_cj_iptv_status_list = []
    channel_cj_iptv_public_ips_list = []

    cpaas_names_list = []
    cpaas_ids_list = []
    cpaas_type_list = []
    cpaas_status_list = []
    cpaas_public_ips_list = []

    # EC2 인스턴스 중 이름에 "web-was-vod"가 포함된 인스턴스들을 필터링합니다.
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name' and 'web-was-vod' in tag['Value']:
                        channel_cj_vod_name = instance['Tags'][0]['Value'][:25] + '...' if len(instance['Tags'][0]['Value']) > 25 else instance['Tags'][0]['Value']
                        channel_cj_vod_names_list.append(channel_cj_vod_name)
                        channel_cj_vod_ids_list.append(instance['InstanceId'])
                        channel_cj_vod_type_list.append(instance['InstanceType'])
                        channel_cj_vod_status_list.append(instance['State']['Name'])
                        channel_cj_vod_public_ips_list.append(instance['PublicIpAddress'] if 'PublicIpAddress' in instance else '-')
                    elif tag['Key'] == 'Name' and 'web-was-iptv' in tag['Value']:
                        channel_cj_iptv_name = instance['Tags'][0]['Value'][:25] + '...' if len(instance['Tags'][0]['Value']) > 25 else instance['Tags'][0]['Value']
                        channel_cj_iptv_names_list.append(channel_cj_iptv_name)
                        channel_cj_iptv_ids_list.append(instance['InstanceId'])
                        channel_cj_iptv_type_list.append(instance['InstanceType'])
                        channel_cj_iptv_status_list.append(instance['State']['Name'])
                        channel_cj_iptv_public_ips_list.append(instance['PublicIpAddress'] if 'PublicIpAddress' in instance else '-')
                    elif tag['Key'] == 'Name' and 'web-was-cpaas' in tag['Value']:
                        cpaas_name = instance['Tags'][0]['Value'][:25] + '...' if len(instance['Tags'][0]['Value']) > 25 else instance['Tags'][0]['Value']
                        cpaas_names_list.append(cpaas_name)
                        cpaas_ids_list.append(instance['InstanceId'])
                        cpaas_type_list.append(instance['InstanceType'])
                        cpaas_status_list.append(instance['State']['Name'])
                        cpaas_public_ips_list.append(instance['PublicIpAddress'] if 'PublicIpAddress' in instance else '-')
                    else:
                        pass
    
    # 인스턴스 이름과 ID 문자열로 변환
    channel_cj_vod_names_str = "\n".join(channel_cj_vod_names_list)
    channel_cj_vod_ids_str = "\n".join(channel_cj_vod_ids_list)
    channel_cj_vod_types_str = "\n".join(channel_cj_vod_type_list)
    channel_cj_vod_states_str = "\n".join(channel_cj_vod_status_list)
    channel_cj_vod_public_ips_str = "\n".join(channel_cj_vod_public_ips_list)
    channel_cj_vod_count = len(channel_cj_vod_names_list)

    channel_cj_iptv_names_str = "\n".join(channel_cj_iptv_names_list)
    channel_cj_iptv_ids_str = "\n".join(channel_cj_iptv_ids_list)
    channel_cj_iptv_types_str = "\n".join(channel_cj_iptv_type_list)
    channel_cj_iptv_states_str = "\n".join(channel_cj_iptv_status_list)
    channel_cj_iptv_public_ips_str = "\n".join(channel_cj_iptv_public_ips_list)
    channel_cj_iptv_count = len(channel_cj_iptv_names_list)

    cpaas_names_str = "\n".join(cpaas_names_list)
    cpaas_ids_str = "\n".join(cpaas_ids_list)
    cpaas_types_str = "\n".join(cpaas_type_list)
    cpaas_states_str = "\n".join(cpaas_status_list)
    cpaas_public_ips_str = "\n".join(cpaas_public_ips_list)
    cpaas_count = len(cpaas_names_list)

    channel_cj_vod = [channel_cj_vod_count, channel_cj_vod_names_str, channel_cj_vod_ids_str, channel_cj_vod_types_str, channel_cj_vod_states_str, channel_cj_vod_public_ips_str]
    channel_cj_iptv = [channel_cj_iptv_count, channel_cj_iptv_names_str, channel_cj_iptv_ids_str, channel_cj_iptv_types_str, channel_cj_iptv_states_str, channel_cj_iptv_public_ips_str]
    cpaas = [cpaas_count, cpaas_names_str, cpaas_ids_str, cpaas_types_str, cpaas_states_str, cpaas_public_ips_str]
    print(channel_cj_vod)
    print(channel_cj_iptv)
    return channel_cj_vod, channel_cj_iptv, cpaas