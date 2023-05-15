import boto3
from datetime import datetime
from credential import *

def simple_storage_service(account):
    session = aws_credential(account)
    # boto3 S3 클라이언트 생성
    s3 = session.client('s3')

    # S3 버킷 리스트 가져오기
    response = s3.list_buckets()

    # S3 버킷 이름 리스트 생성
    bucket_name_list = []

    # S3 버킷 리전 리스트 생성
    bucket_region_list = []

    # S3 버킷 생성 일자 리스트 생성
    bucket_create_date_list = []


    # 각 버킷의 정보를 출력
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        if len(bucket_name) <= 50:
            bucket_name_list.append(bucket['Name'])
        else:
            bucket_name_list.append(bucket['Name'][:50] + '...   ')
        
        creation_date = bucket['CreationDate']
        bucket_create_date_list.append(creation_date.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
            bucket_region_list.append(location if location is not None else "Unknown")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                bucket_region_list.append("AccessDenied")
            else:
                bucket_region_list.append("Unknown")

    # S3 수
    s3_count = len(bucket_name_list)

    # 인스턴스 이름과 ID 문자열로 변환
    bucket_name_str = "\n".join(bucket_name_list)
    bucket_region_str = "\n".join(bucket_region_list)
    bucket_create_date_str = "\n".join(bucket_create_date_list)
    return s3_count, bucket_name_str, bucket_region_str, bucket_create_date_str