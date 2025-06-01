#!/usr/bin/env python3
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
)
from constructs import Construct


class DbStorageStack(Stack):
    """
    DynamoDBとS3リソースを管理するスタック
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDBテーブルの作成
        # 注: パーティションキーやソートキーは要件に応じて変更してください
        self.table = dynamodb.Table(
            self, 
            "FactifyTable",
            table_name="factify-dynamodb-table",
            partition_key=dynamodb.Attribute(
                name="id", 
                type=dynamodb.AttributeType.STRING
            ),
            
            # 課金モード
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            
            # 削除ポリシー
            # DEBUG: 本番では SNAPSHOT/RETAIN
            removal_policy=RemovalPolicy.DESTROY,
        )

        # S3バケットの作成
        self.bucket = s3.Bucket(
            self, 
            "FactifyBucket",
            bucket_name="factify-s3-bucket",
            
            # 暗号化
            encryption=s3.BucketEncryption.S3_MANAGED,
            
            # 削除ポリシ
            # DEBUG: 本番では SNAPSHOT/RETAIN
            removal_policy=RemovalPolicy.DESTROY,
            
            # パブリックアクセスをブロック（セキュリティのベストプラクティス）
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
