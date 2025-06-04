from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_applicationautoscaling as appscaling,
    CfnOutput,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

from constructs import Construct

class FastapiFargateCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, db_storage_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. VPC (Virtual Private Cloud) - 最小構成でコスト削減
        # パブリックサブネットのみの最シンプル構成
        vpc = ec2.Vpc(self, "FastApiVpc",
            max_azs=1,  # Single AZでコスト削減
            nat_gateways=0,  # NAT Gateway削除（$45.2/月削減）
            cidr="10.20.0.0/16",  # 既存VPCと重複しない新しいCIDR
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
                # プライベートサブネット削除でさらにシンプル化
            ]
        )

        # 2. ECS Cluster
        # ECSはコンテナ化されたアプリケーションを実行するためのサービス
        # cluster はコンテナを配置する複数の EC2, Fargate 等で構成される要素
        # https://envader.plus/article/180
        cluster = ecs.Cluster(self, "FastApiCluster",
            vpc=vpc,   # 所属するVPCを指定
            cluster_name="fastapi-cluster"
        )

        # 3. Docker Image Asset
        # ローカルの Dockerfile とソースコードから Docker イメージをビルドし、ECR にプッシュするためのアセット
        image_asset = DockerImageAsset(self, 'FastApiDockerImage', 
            directory='../api'
        )

        # 5. Task Definition
        # タスク定義は、ECS Fargate で実行されるコンテナの設定を定義する
        # https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateTaskDefinition.html
        task_definition = ecs.FargateTaskDefinition(self, "FastApiTaskDef",
            memory_limit_mib=512, # タスクに割り当てるメモリ
            cpu=256 # タスクに割り当てるCPUユニット数
        )

        # 6. Container Definition
        # タスク定義にコンテナを追加する
        container = task_definition.add_container("FastApiContainer",
            image=ecs.ContainerImage.from_docker_image_asset(image_asset),  # ECR からのイメージを指定
            memory_limit_mib=512,  # コンテナに割り当てるメモリ
            logging=ecs.LogDrivers.aws_logs(stream_prefix="fastapi")  # CloudWatch Logs にログを送信
        )

        # コンテナのポートマッピングを設定
        container.add_port_mappings(
            ecs.PortMapping(container_port=80, host_port=80, protocol=ecs.Protocol.TCP)
        )

        # 7. Security Group for ECS Service (ALB削除してパブリックアクセス用に変更)
        # ECS サービスのセキュリティグループを定義（インターネットからの直接アクセスを許可）
        ecs_security_group = ec2.SecurityGroup(self, "ECSSecurityGroup",
            vpc=vpc,
            description="Security group for ECS service - direct access",
            allow_all_outbound=True
        )
        # インターネットからのHTTPトラフィックを直接許可
        ecs_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from anywhere"
        )

        # 8. ECS Fargate Service (ALB削除 - パブリックアクセス版)
        # Fargate サービスを作成し、ECS クラスターにタスク定義をデプロイ
        service = ecs.FargateService(self, "FastApiService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=0,  # 初期状態は0（開発時間外）
            security_groups=[ecs_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),  # パブリックサブネットで実行
            assign_public_ip=True  # パブリックIPアドレスを割り当て
        )

        # 9. Auto Scaling設定（開発時間帯のみ稼働）
        # Application Auto Scalingターゲットを作成
        scalable_target = service.auto_scale_task_count(
            min_capacity=0,  # 最小タスク数（開発時間外）
            max_capacity=1   # 最大タスク数（開発時間内）
        )
        
        # 時間ベースのスケーリング - 平日9時から18時まで稼働
        # 稼働開始：平日9時（JST）= UTC 0時
        scalable_target.scale_on_schedule("ScaleUpSchedule",
            schedule=appscaling.Schedule.cron(
                hour="0",    # UTC 0時 = JST 9時
                minute="0",
                week_day="MON-FRI"
            ),
            min_capacity=1,
            max_capacity=1
        )
        
        # 稼働停止：平日18時（JST）= UTC 9時
        scalable_target.scale_on_schedule("ScaleDownSchedule",
            schedule=appscaling.Schedule.cron(
                hour="9",    # UTC 9時 = JST 18時
                minute="0",
                week_day="MON-FRI"
            ),
            min_capacity=0,
            max_capacity=0
        )
        # 10. DbStorageStackが指定されている場合、タスクロールにS3とDynamoDBへのアクセス権限を付与
        if db_storage_stack:
            db_storage_stack.grant_access_to_task_role(task_definition.task_role)

        # 11. Output - ECS Service情報（ALB削除のため直接IPアクセス）
        CfnOutput(self, "ECSServiceInfo",
            value="ECS Service deployed - Check CloudWatch for public IP",
            description="ECS Service deployed without ALB - access via task public IP"
        )

        # Store API endpoint placeholder (no fixed endpoint without ALB)
        self.api_endpoint = "http://DYNAMIC_ECS_IP"