from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_apigatewayv2_alpha as apigw,
    aws_apigatewayv2_integrations_alpha as integrations,
    aws_iam as iam,
    Duration,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

from constructs import Construct

class FastapiFargateCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. ECR Repository (変更なし)
        repository = ecr.Repository(self, "FastApiAppRepository",
            repository_name="fastapi-app",
        )

        # ... (他のリソース定義もここに続きます)

        # DockerImageAssetの directory 引数を修正します
        # 以前: directory='./api' (これはCDKプロジェクトルートからの相対パスだった)
        # 変更後: '../api' (infraディレクトリからの相対パス)
        image_asset = DockerImageAsset(self, 'FastApiDockerImage', directory='../api')

        # ... (Fargate Serviceの定義など、他の部分は続きます)