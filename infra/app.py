#!/usr/bin/env python3
import os

from aws_cdk import core
from infra.vpc_stack import FastApiVpcStack

app = core.App()

# AWSアカウントIDとリージョンは環境変数から取得
# 例: export AWS_ACCOUNT_ID="YOUR_AWS_ACCOUNT_ID"
#     export AWS_REGION="ap-northeast-1"
env = core.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "ap-northeast-1")
)

# VPCスタックの作成
vpc_stack = FastApiVpcStack(app, "FastApiVpcStack", env=env)

app.synth()
