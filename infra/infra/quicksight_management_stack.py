import json
from aws_cdk import (
    Stack,
    aws_quicksight as quicksight,
    aws_iam as iam,
    CfnOutput,
    CustomResource,
    aws_lambda as lambda_,
    Duration,
)
from constructs import Construct


class QuickSightManagementStack(Stack):
    """QuickSight Standard Editionの設定とデータソース管理"""

    def __init__(self, scope: Construct, construct_id: str, 
                 auth_stack=None, db_storage_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 前提条件チェック
        if not auth_stack:
            raise ValueError("auth_stack parameter is required")

        # QuickSight設定用のLambda関数を作成
        self.quicksight_setup_lambda = lambda_.Function(
            self, "QuickSightSetupLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            timeout=Duration.minutes(5),
            code=lambda_.Code.from_inline(self._get_lambda_code()),
            environment={
                "IDENTITY_POOL_ID": auth_stack.identity_pool.ref,
                "USER_POOL_ID": auth_stack.user_pool.user_pool_id,
                "REGION": self.region
            }
        )

        # Lambda実行用のIAMポリシー
        self.quicksight_setup_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "quicksight:*",
                    "dynamodb:ListTables",
                    "dynamodb:DescribeTable",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "iam:ListRoles",
                    "iam:PassRole"
                ],
                resources=["*"]
            )
        )

        # カスタムリソースでQuickSight設定を実行
        self.quicksight_setup = CustomResource(
            self, "QuickSightSetupCustomResource",
            service_token=self.quicksight_setup_lambda.function_arn,
            properties={
                "StackName": self.stack_name,
                "Region": self.region
            }
        )

        # データソース設定（DynamoDBテーブルが存在する場合）
        if db_storage_stack:
            self._create_dynamodb_data_source(db_storage_stack)

        # 出力
        CfnOutput(
            self, "QuickSightConsoleUrl",
            value=f"https://{self.region}.quicksight.aws.amazon.com/sn/start",
            description="QuickSight Console URL"
        )

    def _create_dynamodb_data_source(self, db_storage_stack):
        """DynamoDB用のQuickSightデータソースを作成"""
        
        # データソース用のIAMロール
        data_source_role = iam.Role(
            self, "QuickSightDataSourceRole",
            assumed_by=iam.ServicePrincipal("quicksight.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSQuickSightDynamoDBAccess")
            ]
        )

        # DynamoDBテーブルへの読み取りアクセスを追加
        if hasattr(db_storage_stack, 'metadata_table'):
            data_source_role.add_to_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:GetItem",
                        "dynamodb:BatchGetItem",
                        "dynamodb:DescribeTable"
                    ],
                    resources=[db_storage_stack.metadata_table.table_arn]
                )
            )

    def _get_lambda_code(self) -> str:
        """QuickSight設定用のLambda関数コード"""
        return '''
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """QuickSight Account登録とユーザー作成"""
    
    try:
        request_type = event['RequestType']
        logger.info(f"Request type: {request_type}")
        
        if request_type == 'Create':
            return create_quicksight_account(event, context)
        elif request_type == 'Delete':
            return delete_quicksight_resources(event, context)
        else:
            return {
                'Status': 'SUCCESS',
                'Data': {}
            }
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'Status': 'FAILED',
            'Reason': str(e)
        }

def create_quicksight_account(event, context):
    """QuickSightアカウントを作成"""
    
    quicksight = boto3.client('quicksight')
    region = event['ResourceProperties']['Region']
    account_id = context.invoked_function_arn.split(':')[4]
    
    try:
        # QuickSightアカウントの状態を確認
        try:
            response = quicksight.describe_account_settings(AwsAccountId=account_id)
            logger.info("QuickSight account already exists")
            account_name = response['AccountSettings']['AccountName']
        except quicksight.exceptions.ResourceNotFoundException:
            # アカウントが存在しない場合は作成
            logger.info("Creating QuickSight account")
            
            # アカウント作成（Standard Edition）
            quicksight.create_account_subscription(
                AwsAccountId=account_id,
                AccountName=f"factify-quicksight-{account_id[:8]}",
                NotificationEmail="admin@example.com",  # 実際の管理者メールに変更
                Edition="STANDARD",
                AuthenticationMethod="IDENTITY_POOL"
            )
            
            account_name = f"factify-quicksight-{account_id[:8]}"
            logger.info(f"QuickSight account created: {account_name}")
        
        return {
            'Status': 'SUCCESS',
            'Data': {
                'AccountName': account_name,
                'AccountId': account_id,
                'Region': region
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create QuickSight account: {str(e)}")
        raise e

def delete_quicksight_resources(event, context):
    """QuickSightリソースをクリーンアップ"""
    
    logger.info("QuickSight resources cleanup - manual deletion required")
    
    return {
        'Status': 'SUCCESS',
        'Data': {}
    }
'''

    def create_sample_dashboard(self):
        """サンプルダッシュボードの作成手順を出力"""
        
        CfnOutput(
            self, "SampleDashboardInstructions",
            value=json.dumps({
                "step1": "QuickSightコンソールにアクセス",
                "step2": "新しいデータセットを作成",
                "step3": "DynamoDBデータソースを選択",
                "step4": "テーブルを選択してインポート",
                "step5": "ダッシュボードを作成"
            }, indent=2),
            description="Sample dashboard creation instructions"
        )
