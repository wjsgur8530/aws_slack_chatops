import os
import boto3
from credential import *

def ec2_count(account):
    session = aws_credential(account)

    # EC2 client 생성
    ec2_client = session.client('ec2')

    # 인스턴스 상태 가져오기
    response = ec2_client.describe_instances()

    # 인스턴스 수 계산
    instance_count = sum(len(reservation['Instances']) for reservation in response['Reservations']) 

    # 인스턴스 이름 리스트 생성
    instance_names = []

    # 인스턴스 ID 리스트 생성
    instance_ids = []

    # 인스턴스 타입 리스트 생성
    instance_types = []

    # 인스턴스 상태 리스트 생성
    instance_states = []

    # 인스턴스 퍼블릭 아이피 리스트 생성
    instance_public_ips = []

    # 인스턴스 운영체제 타입 리스트 생성
    instance_os_types = []

    # 인스턴스 이름 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                instance_name = instance['Tags'][0]['Value']
                if len(instance_name) <= 25:
                    instance_names.append(instance_name)
                else:
                    instance_names.append(instance_name[:25] + '...   ')
            else:
                instance_names.append("-")

    # 인스턴스 ID 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    # 인스턴스 타입 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_types.append(instance['InstanceType'])

    # 인스턴스 상태 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_states.append(instance['State']['Name'])

    # 인스턴스 IP 주소 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'PublicIpAddress' in instance:
                instance_public_ips.append(instance['PublicIpAddress'])
            else:
                instance_public_ips.append('-')

    # 인스턴스 OS 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            # Platform이 가질 수 있는 속성은 Windows와 None 뿐이다.
            platform = response['Reservations'][0]['Instances'][0].get('Platform', 'None')
            # 인스턴스의 운영 체제 결정
            if platform == 'windows':
                os_type = 'Windows'
            else:
                os_type = 'Linux/UNIX'
            # 인스턴스의 운영 체제 정보 추가
            instance_os_types.append(os_type)

    # 인스턴스 이름과 ID 문자열로 변환
    instance_names_str = "\n".join(instance_names)
    instance_ids_str = "\n".join(instance_ids)
    instance_types_str = "\n".join(instance_types)
    instance_states_str = "\n".join(instance_states)
    instance_public_ips_str = "\n".join(instance_public_ips)
    instance_os_types_str = "\n".join(instance_os_types)

    return instance_count, instance_names_str, instance_ids_str, instance_types_str, instance_states_str, instance_public_ips_str, instance_os_types_str, instance_names, instance_states

# 태그 이름과 값으로 EC2 인스턴스 개수 가져오기
# ec2_count('Name', 'hyuk-test-ec2')

def instance_count_len(account):
    session = aws_credential(account)
    # EC2 client 생성
    ec2_client = session.client('ec2')
    # 인스턴스 상태 가져오기
    response = ec2_client.describe_instances()
    # 인스턴스 수 계산
    instance_count = sum(len(reservation['Instances']) for reservation in response['Reservations']) 
    return instance_count

def instance_ids_list(account):
    session = aws_credential(account)
    # EC2 client 생성
    ec2_client = session.client('ec2')
    # 인스턴스 상태 가져오기
    response = ec2_client.describe_instances()
    # 인스턴스 ID 리스트 생성
    instance_ids = []
    # 인스턴스 ID 추가
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    return instance_ids

