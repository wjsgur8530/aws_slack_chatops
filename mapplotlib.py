#%%
import boto3
import matplotlib.pyplot as plt
from credential import *
import datetime
import pytz

# 한국 표준시 설정
KST = pytz.timezone('Asia/Seoul')

def matplotlib_cpu_image(instance_id, account):
    # CloudWatch 클라이언트 생성
    session = aws_credential(account)

    cloudwatch = session.client('cloudwatch')

    # 메트릭 데이터 조회
    now = datetime.datetime.now(tz=pytz.utc).astimezone(KST)
    utc_offset = datetime.timedelta(hours=9)
    start_time = (now - datetime.timedelta(hours=1)).isoformat()
    end_time = now.isoformat()
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True
            },
        ],
        StartTime=start_time,
        EndTime=end_time
    )

    timestamps = response['MetricDataResults'][0]['Timestamps']
    values = response['MetricDataResults'][0]['Values']

    print(response)

    # 그래프 생성
    timestamps_kst = [timestamp.astimezone(KST) for timestamp in timestamps]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps_kst, values)
    plt.xlabel('Time')
    plt.ylabel('CPU Utilization (%)')
    plt.title('EC2 CPU Utilization')
    plt.show()
    plt.savefig('./graph/cpu_util.png')
    graph_image = './graph/cpu_util.png'

    return graph_image

def matplotlib_memory_image(instance_id, account):
    # CloudWatch 클라이언트 생성
    session = aws_credential(account)

    cloudwatch = session.client('cloudwatch')
    # 메트릭 데이터 조회
    now = datetime.datetime.now(tz=pytz.utc).astimezone(KST)
    utc_offset = datetime.timedelta(hours=9)
    start_time = (now - datetime.timedelta(hours=1)).isoformat()
    end_time = now.isoformat()
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': 'mem_used_percent',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True
            },
        ],
        StartTime=start_time,
        EndTime=end_time
    )

    timestamps = response['MetricDataResults'][0]['Timestamps']
    values = response['MetricDataResults'][0]['Values']

    round_values = []
    for value in values:
        round_values.append(round(value, 5))


    print(round_values)
    # 그래프 생성
    timestamps_kst = [timestamp.astimezone(KST) for timestamp in timestamps]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps_kst, round_values)
    plt.xlabel('Time')
    plt.ylabel('Memory Used Percent (%)')
    plt.title('EC2 Memory Used Percent')
    plt.show()
    plt.savefig('./graph/memory_usage.png')
    graph_image = './graph/memory_usage.png'

    return graph_image

def matplotlib_disk_image(instance_id, account):
    # CloudWatch 클라이언트 생성
    session = aws_credential(account)

    cloudwatch = session.client('cloudwatch')
    # 메트릭 데이터 조회
    now = datetime.datetime.now(tz=pytz.utc).astimezone(KST)
    utc_offset = datetime.timedelta(hours=9)
    start_time = (now - datetime.timedelta(hours=1)).isoformat()
    end_time = now.isoformat()
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'disk_used_percent',
                        'Dimensions': [
                            {
                                'Name': 'InstanceId',
                                'Value': instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                    'Unit': 'Percent'
                },
                'ReturnData': True
            },
        ],
        StartTime=start_time,
        EndTime=end_time
    )

    timestamps = response['MetricDataResults'][0]['Timestamps']
    values = response['MetricDataResults'][0]['Values']

    # 그래프 생성
    timestamps_kst = [timestamp.astimezone(KST) for timestamp in timestamps]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps_kst, values)
    plt.xlabel('Time')
    plt.ylabel('Disk Used Percent (%)')
    plt.title('EC2 Disk Used Percent')
    plt.show()
    plt.savefig('./graph/disk_bytes.png')
    graph_image = './graph/disk_bytes.png'

    return graph_image


def cloudwatch_url(instance_id):
    # 메트릭 데이터 조회
    region = 'ap-northeast-2'

    # CloudWatch URL 생성
    url = f'https://console.aws.amazon.com/cloudwatch/home?region={region}'
    return url

