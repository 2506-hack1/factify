#!/usr/bin/env python3
import os

import aws_cdk as cdk

# 元のインポート: from fastapi_fargate_cdk.fastapi_fargate_cdk_stack import FastapiFargateCdkStack
# ディレクトリ構造変更後のインポート
from infra.fastapi_fargate_cdk_stack import FastapiFargateCdkStack
from infra.db_storage_stack import DbStorageStack
from infra.s3_cloudfront_stack import S3CloudFrontStack
from infra.cognito_auth_stack import CognitoAuthStack
from infra.opensearch_stack import OpenSearchStack

app = cdk.App()
target_env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region="ap-northeast-1"
)

# Cognito認証スタック（新規追加）
cognito_stack = CognitoAuthStack(app, "CognitoAuthStack",
    env=target_env,
)

db_storage_stack = DbStorageStack(app, "DbStorageStack",
    env=target_env,
)

# OpenSearch検索エンジンスタック（新規追加）
opensearch_stack = OpenSearchStack(app, "OpenSearchStack",
    env=target_env,
)

fastapi_stack = FastapiFargateCdkStack(app, "FastapiFargateCdkStack",
    env=target_env,
    db_storage_stack=db_storage_stack,
    cognito_stack=cognito_stack,
)

# S3 + CloudFront stack for React webapp
S3CloudFrontStack(app, "S3CloudFrontStack",
    env=target_env,
    api_endpoint=fastapi_stack.api_endpoint,
)

app.synth()