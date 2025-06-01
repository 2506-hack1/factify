#!/usr/bin/env python3
import os

import aws_cdk as cdk

# 元のインポート: from fastapi_fargate_cdk.fastapi_fargate_cdk_stack import FastapiFargateCdkStack
# ディレクトリ構造変更後のインポート
from infra.fastapi_fargate_cdk_stack import FastapiFargateCdkStack
from infra.db_storage_stack import DbStorageStack

app = cdk.App()
target_env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region="ap-northeast-1"
)

FastapiFargateCdkStack(app, "FastapiFargateCdkStack",
    env=target_env,
)

DbStorageStack(app, "DbStorageStack",
    env=target_env,
)

app.synth()