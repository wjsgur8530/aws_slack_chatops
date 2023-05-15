import boto3
from credential import *

def database_rds(account):
    session = aws_credential(account)

    # RDS 클라이언트를 초기화합니다.
    rds = session.client('rds')

    # RDS 식별자 리스트 생성
    rds_identifier_list = []

    # RDS 엔진 리스트 생성
    rds_engine_list = []

    # RDS 사이즈(타입) 리스트 생성
    rds_size_list = []

    # RDS 상태 리스트 생성
    rds_status_list = []

    # RDS 역할 리스트 생성
    rds_role_list = []


    # 모든 RDS DB 인스턴스를 가져와서 반복합니다.
    for instance in rds.describe_db_instances()['DBInstances']:
        rds_identifier_list.append(instance['DBInstanceIdentifier'])
        rds_engine_list.append(instance['Engine'])
        rds_size_list.append(instance['DBInstanceClass'])
        rds_status_list.append(instance['DBInstanceStatus'])

        # DB 인스턴스가 복제본인지 여부를 확인합니다.
        if 'ReadReplicaSourceDBInstanceIdentifier' in instance:
            db_role = 'Read Replica  '
            rds_role_list.append(db_role)
        else:
            db_role = 'Primary'
            rds_role_list.append(db_role)


    # RDS 수
    rds_count = len(rds_identifier_list)

    # 인스턴스 이름과 ID 문자열로 변환
    rds_identifier_str = "\n".join(rds_identifier_list)
    rds_engine_str = "\n".join(rds_engine_list)
    rds_size_str = "\n".join(rds_size_list)
    rds_status_str = "\n".join(rds_status_list)
    rds_role_str = "\n".join(rds_role_list)
    
    return rds_count, rds_identifier_str, rds_engine_str, rds_size_str, rds_status_str, rds_role_str
