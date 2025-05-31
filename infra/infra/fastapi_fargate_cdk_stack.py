from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

from constructs import Construct

class FastapiFargateCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. VPC (Virtual Private Cloud)
        # リソース全体を囲むネットワーク
        # https://envader.plus/article/76
        vpc = ec2.Vpc(self, "FastApiVpc",
            max_azs=2,  # 2つのアベイラビリティゾーンを使用
            nat_gateways=1  # コスト削減のためNAT Gatewayは1つ
        )

        # 2. ECS Cluster
        # ECSはコンテナ化されたアプリケーションを実行するためのサービス
        # cluster はコンテナを配置する複数の EC2, Fargate 等で構成される要素
        # https://envader.plus/article/180
        cluster = ecs.Cluster(self, "FastApiCluster",
            vpc=vpc,   # 所属するVPCを指定
            cluster_name="fastapi-cluster"
        )

        # 3. ECR Repository
        # ECRはDockerイメージを保存するためのサービス
        # ここでのリポジトリは、Docker イメージ等を保存するスペースを指す
        # https://qiita.com/shate/items/a24ae736bcd91787801c
        repository = ecr.Repository(self, "FastApiAppRepository",
            repository_name="fastapi-app",
        )

        # 4. Docker Image Asset
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

        # 7. Security Group for ALB
        # ALB はロードバランサーで、トラフィックを ECS サービスに分散する
        # セキュリティグループは、VPC 内のリソース間のトラフィックを制御するためのファイアウォールルールを定義する
        alb_security_group = ec2.SecurityGroup(self, "ALBSecurityGroup",
            vpc=vpc,
            description="Security group for ALB",
            allow_all_outbound=True
        )
        # 全体的に HTTP トラフィックを許可
        alb_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic from anywhere"
        )

        # 8. Security Group for ECS Service
        # ECS サービスのセキュリティグループを定義（ALB からのトラフィックを許可）
        ecs_security_group = ec2.SecurityGroup(self, "ECSSecurityGroup",
            vpc=vpc,
            description="Security group for ECS service",
            allow_all_outbound=True
        )
        # ALB からのトラフィックを許可
        ecs_security_group.add_ingress_rule(
            alb_security_group,
            ec2.Port.tcp(80),
            "Allow traffic from ALB"
        )

        # 9. Application Load Balancer
        # ALB を作成し、インターネットからのトラフィックを受け入れる
        alb = elbv2.ApplicationLoadBalancer(self, "FastApiALB",
            vpc=vpc,
            internet_facing=True,  # インターネットからのアクセスを許可
            load_balancer_name="fastapi-alb",
            security_group=alb_security_group
        )

        # 10. Target Group
        # ターゲットグループは、ALB がトラフィックをルーティングする ECS サービスを定義する
        target_group = elbv2.ApplicationTargetGroup(self, "FastApiTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,  
            target_type=elbv2.TargetType.IP, # ターゲットのタイプを IP に設定（Fargate では IP アドレスが使用される）
            health_check=elbv2.HealthCheck(  # ヘルスチェックの設定
                path="/",  # ヘルスチェックのパス
                healthy_http_codes="200"  # ヘルスチェックが成功する HTTP ステータスコード
            )
        )

        # 11. ALB Listener
        # ALB が受け取るトラフィックを処理するためのエンドポイントを作成
        listener = alb.add_listener("FastApiListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group]
        )

        # 12. ECS Fargate Service
        # Fargate サービスを作成し、ECS クラスターにタスク定義をデプロイ
        service = ecs.FargateService(self, "FastApiService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,  # デプロイするタスクの数
            security_groups=[ecs_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)  # プライベートサブネットで実行
        )

        # サービスをターゲットグループに登録
        service.attach_to_application_target_group(target_group)

        # 13. Output - ALB URL
        CfnOutput(self, "LoadBalancerUrl",
            value=f"http://{alb.load_balancer_dns_name}",
            description="URL of the load balancer"
        )