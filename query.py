

def aws_query():
    # aws query 리스트 생성
    aws_query_list = [
        "`계정` `조회 계정 선택 명령어`",
        "`리소스 상태 조회` `리소스 상태 조회 명령어`",
        "`리소스 현황 조회` `리소스 현황 조회 명령어`",
        "`전체` `전체 리소스 현황 조회 명령어`",
        "`EC2` `EC2 리소스 현황 조회 명령어`",
        "`RDS` `RDS 리소스 현황 조회 명령어`",
        "`ELB` `ELB 리소스 현황 조회 명령어`",
        "`S3` `S3 리소스 현황 조회 명령어`",
        "`VPC` `VPC 리소스 현황 조회 명령어`",
        "`채널CJ VOD` `채널CJ VOD 리소스 현황 조회`",
        "`채널CJ IPTV` `채널CJ IPTV 리소스 현황 조회`",
        "`CPAAS` `CPAAS 리소스 현황 조회`"
    ]
    aws_query_list_str = "\n".join(aws_query_list)

    return aws_query_list_str

    
