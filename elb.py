import boto3
from credential import *

def elastic_loadbalancer(account):
    session = aws_credential(account)
    
    # 로드밸런서 이름 리스트 생성
    loadbalancer_name_list = []

    # 로드밸런서 DNS 이름 리스트 생성
    loadbalancer_dns_list = []

    # 로드밸런서 State 리스트 생성
    loadbalancer_state_list = []

    # 로드밸런서 Type 리스트 생성
    loadbalancer_type_list = []


    # ELB 클라이언트를 초기화합니다.
    elb = session.client('elbv2')

    # 모든 ELB를 가져와서 반복합니다.
    for lb in elb.describe_load_balancers()['LoadBalancers']:
        loadbalancer_name_list.append(lb['LoadBalancerName'])
        loadbalancer_dns_list.append(lb['DNSName'])
        loadbalancer_state_list.append(lb['State']['Code'])
        loadbalancer_type_list.append(lb['Type'])
    
    # RDS 수
    elb_count = len(loadbalancer_name_list)

    # 인스턴스 이름과 ID 문자열로 변환
    loadbalancer_name_str = "\n".join([f"{lb_name}  " for lb_name in loadbalancer_name_list])
    loadbalancer_dns_str = "\n".join([f"{lb_dns}  " for lb_dns in loadbalancer_dns_list])
    loadbalancer_state_str = "\n".join([f"{lb_state}  " for lb_state in loadbalancer_state_list])
    loadbalancer_type_str = "\n".join([f"{lb_type}  " for lb_type in loadbalancer_type_list])

    print(loadbalancer_name_str)

    return elb_count, loadbalancer_name_str, loadbalancer_dns_str, loadbalancer_state_str, loadbalancer_type_str