import boto3
from credential import *

def vpc_counts(account):
    # AWS Session 설정
    session = aws_credential(account)

    # EC2 client 생성
    ec2 = session.client('ec2')

    # VPC 이름 리스트 생성
    vpc_name_list = []

    # VPC 상태 리스트 생성
    vpc_state_list = []

    # VPC 목록 및 개수 가져오기
    vpcs = ec2.describe_vpcs()
    vpc_count = len(vpcs['Vpcs'])

    # VPC 개수 및 목록 출력
    for vpc in vpcs['Vpcs']:
        vpc_name_list.append(vpc['VpcId'])
        vpc_state_list.append(vpc['State'])

    vpc_name_list_str = "\n".join([f"{vpc_name}  " for vpc_name in vpc_name_list])
    vpc_state_list_str = "\n".join([f"{vpc_state}  " for vpc_state in vpc_state_list])

    return vpc_count, vpc_name_list_str, vpc_state_list_str