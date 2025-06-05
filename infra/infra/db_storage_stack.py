#!/usr/bin/env python3
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    CfnOutput,
)
from constructs import Construct


class DbStorageStack(Stack):
    """
    DynamoDBとS3リソースを管理するスタック
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDBテーブルの作成
        self.table = dynamodb.Table(
            self, 
            "FactifyTable",
            table_name=f"factify-dynamodb-table-{self.account}-{self.region}",
            partition_key=dynamodb.Attribute(
                name="id", 
                type=dynamodb.AttributeType.STRING  # UUID
            ),
            
            # 課金モード
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            
            # 削除ポリシー
            # DEBUG: 本番では SNAPSHOT/RETAIN
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # GSI（Global Secondary Index）の追加    
        # タイトルによる検索を効率化するためのインデックス
        self.table.add_global_secondary_index(
            index_name="TitleIndex",
            partition_key=dynamodb.Attribute(
                name="title",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # S3バケットの作成
        self.bucket = s3.Bucket(
            self, 
            "FactifyBucket",
            bucket_name=f"factify-s3-bucket-{self.account}-{self.region}",
            
            # 暗号化
            encryption=s3.BucketEncryption.S3_MANAGED,
            
            # 削除ポリシ
            # DEBUG: 本番では SNAPSHOT/RETAIN
            removal_policy=RemovalPolicy.DESTROY,
            
            # パブリックアクセスをブロック（セキュリティのベストプラクティス）
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Outputs for CloudFormation
        CfnOutput(
            self,
            "DataS3BucketName",
            value=self.bucket.bucket_name,
            description="Data Storage S3 Bucket Name"
        )

        CfnOutput(
            self,
            "DynamoDBTableName", 
            value=self.table.table_name,
            description="DynamoDB Table Name"
        )

    def grant_access_to_task_role(self, task_role):
        """
        指定されたタスクロールにS3バケットとDynamoDBテーブルへのアクセス権限を付与する
        """
        # S3バケットへのアクセス権限を付与
        self.bucket.grant_read_write(task_role)
        
        # DynamoDBテーブルへのアクセス権限を付与
        self.table.grant_read_write_data(task_role)
