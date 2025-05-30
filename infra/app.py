#!/usr/bin/env python3
import os

import aws_cdk as cdk

# 元のインポート: from fastapi_fargate_cdk.fastapi_fargate_cdk_stack import FastapiFargateCdkStack
# ディレクトリ構造変更後のインポート
from infra.fastapi_fargate_cdk_stack import FastapiFargateCdkStack

app = cdk.App()
target_env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region="ap-northeast-1"
)

FastapiFargateCdkStack(app, "FastapiFargateCdkStack",
    env=target_env,
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context will be lazily evaluated
    # at deploy time.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

app.synth()