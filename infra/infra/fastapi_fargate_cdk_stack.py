from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    CfnOutput,
    Duration,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

from constructs import Construct

class FastapiFargateCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, db_storage_stack=None, cognito_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR Repository with lifecycle policy
        ecr_repo = ecr.Repository(self, "FastApiECRRepo",
            repository_name=f"factify-fastapi-{construct_id.lower()}",
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=10,
                    rule_priority=1,
                    description="Keep only 10 latest images"
                )
            ]
        )

        # 1. VPC (Virtual Private Cloud) - API Gateway用にPrivateサブネット追加
        # API Gateway VPC Linkには少なくとも1つのPrivateサブネットが必要
        vpc = ec2.Vpc(self, "FastApiVpc",
            max_azs=2,  # API Gateway VPC Linkには最低2つのAZが推奨
            nat_gateways=1,  # NAT Gateway（$45.2/月だが、VPC Linkには必要）
            ip_addresses=ec2.IpAddresses.cidr("10.20.0.0/16"),  # 既存VPCと重複しない新しいCIDR
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
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

        # 3. Docker Image Asset with optimizations
        # ローカルの Dockerfile とソースコードから Docker イメージをビルドし、ECR にプッシュするためのアセット
        image_asset = DockerImageAsset(self, 'FastApiDockerImage', 
            directory='../api',
            build_args={
                "BUILDKIT_INLINE_CACHE": "1"
            },
            exclude=[
                "**/__pycache__",
                "**/*.pyc",
                "**/.*",
                "**/*.md",
                "**/tests",
                "**/debug"
            ]
        )

        # 5. Task Definition - Increased resources for faster startup
        # タスク定義は、ECS Fargate で実行されるコンテナの設定を定義する
        # https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.FargateTaskDefinition.html
        task_definition = ecs.FargateTaskDefinition(self, "FastApiTaskDef",
            memory_limit_mib=1024, # Increased from 512 for faster startup
            cpu=512 # Increased from 256 for faster startup
        )

        # 6. Container Definition
        # タスク定義にコンテナを追加する
        container_env = {
            "S3_BUCKET_NAME": db_storage_stack.bucket.bucket_name if db_storage_stack else "factify-s3-bucket",
            "DYNAMODB_TABLE_NAME": db_storage_stack.table.table_name if db_storage_stack else "factify-dynamodb-table",
            "REGION_NAME": self.region
        }
        
        # Cognito設定を環境変数として追加
        if cognito_stack:
            container_env.update({
                "COGNITO_REGION": self.region,
                "COGNITO_USER_POOL_ID": cognito_stack.user_pool_id,
                "COGNITO_CLIENT_ID": cognito_stack.user_pool_client_id
            })

        container = task_definition.add_container("FastApiContainer",
            image=ecs.ContainerImage.from_docker_image_asset(image_asset),  # ECR からのイメージを指定
            memory_limit_mib=896,  # コンテナメモリはタスクメモリ(1024MB)より少なく設定
            logging=ecs.LogDrivers.aws_logs(stream_prefix="fastapi"),  # CloudWatch Logs にログを送信
            environment=container_env,
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:80/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                retries=3,
                start_period=Duration.seconds(60)
            )
        )

        # コンテナのポートマッピングを設定
        container.add_port_mappings(
            ecs.PortMapping(container_port=80, host_port=80, protocol=ecs.Protocol.TCP)
        )

        # 8. Security Group for ECS Service (直接アクセス用)
        # ECS サービスのセキュリティグループを定義（インターネットからの直接アクセスを許可）
        ecs_security_group = ec2.SecurityGroup(self, "ECSSecurityGroup",
            vpc=vpc,
            description="Security group for ECS service - Direct Internet access",
            allow_all_outbound=True
        )
        # インターネットからのHTTPトラフィックを許可
        ecs_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from Internet"
        )

        # 9. ECS Fargate Service (直接アクセス版) with optimized deployment
        # Fargate サービスを作成し、ECS クラスターにタスク定義をデプロイ
        service = ecs.FargateService(self, "FastApiService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,  # 常時1つのタスクを稼働
            security_groups=[ecs_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),  # パブリックサブネットで実行
            assign_public_ip=True,  # パブリックIPを割り当て
            # CDK v2では deployment_configuration は直接指定
            max_healthy_percent=200,
            min_healthy_percent=0,  # Allow faster deployments
            enable_execute_command=True  # For debugging
        )
        
        # ECS ServiceをTarget Groupに登録する必要がなくなりました（直接アクセスのため）

        # 11. DbStorageStackが指定されている場合、タスクロールにS3とDynamoDBへのアクセス権限を付与
        if db_storage_stack:
            db_storage_stack.grant_access_to_task_role(task_definition.task_role)

        # 12. Outputs
        # ECSタスクのパブリックIPは動的に変わるため、クラスター情報を出力
        CfnOutput(self, "ECSClusterName",
            value=cluster.cluster_name,
            description="ECS Cluster name to find task public IP"
        )
        
        CfnOutput(self, "ECSServiceName", 
            value=service.service_name,
            description="ECS Service name"
        )

        # Store ECS cluster info for S3CloudFrontStack  
        self.api_endpoint = None  # 直接アクセスのためAPI Gatewayエンドポイントは不要