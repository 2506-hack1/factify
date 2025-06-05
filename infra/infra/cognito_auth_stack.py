from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct


class CognitoAuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 最小限のUser Pool
        self.user_pool = cognito.UserPool(
            self,
            "FactifyUserPool",
            user_pool_name="factify-user-pool",
            
            # 基本設定のみ
            sign_in_aliases=cognito.SignInAliases(email=True),
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            
            # 開発用設定
            removal_policy=RemovalPolicy.DESTROY
        )

        # 基本的なUser Pool Client（SPA用、シークレットなし）
        self.user_pool_client = self.user_pool.add_client(
            "FactifyWebClient",
            user_pool_client_name="factify-web-client",
            generate_secret=False,  # SPA用
            auth_flows=cognito.AuthFlow(
                user_password=True,  # ALLOW_USER_PASSWORD_AUTH フローを有効化
                user_srp=True,       # ALLOW_USER_SRP_AUTH フローも有効化
                admin_user_password=True  # ALLOW_ADMIN_USER_PASSWORD_AUTH フローも有効化
            )
        )

        # Outputs（デバッグ用）
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )

        CfnOutput(
            self,
            "UserPoolClientId", 
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID"
        )

        # 属性をエクスポート（他のスタックで使用）
        self.user_pool_id = self.user_pool.user_pool_id
        self.user_pool_client_id = self.user_pool_client.user_pool_client_id
