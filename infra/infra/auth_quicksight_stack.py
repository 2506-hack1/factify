from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_quicksight as quicksight,
    CfnOutput,
    Duration,
    RemovalPolicy,
)
from constructs import Construct


class AuthQuickSightStack(Stack):
    """Cognito認証とQuickSight Standard Editionを管理するスタック"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Cognito User Pool
        # ユーザーの認証情報を管理するためのユーザープール
        self.user_pool = cognito.UserPool(
            self, "FactifyUserPool",
            user_pool_name="factify-user-pool",
            # サインイン設定
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            # パスワードポリシー
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            # アカウント復旧設定
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            # セルフサインアップを有効化
            self_sign_up_enabled=True,
            # ユーザー招待設定
            user_invitation=cognito.UserInvitationConfig(
                email_subject="Factifyアプリケーションへの招待",
                email_body="{username} 様<br><br>一時パスワードを通知いたします。ログイン後、パスワードを変更してください。<br><br>一時パスワード: {####}<br><br>このメールは自動生成されたものです。返信はできませんのでご注意ください。<br>"
            ),
            # ユーザー検証設定
            user_verification=cognito.UserVerificationConfig(
                email_subject="Factifyアプリケーション - メールアドレス確認",
                email_body="確認コード: {####}",
                email_style=cognito.VerificationEmailStyle.CODE
            ),
            # 削除保護
            # DEBUG: 本番環境ではRETAIN
            removal_policy=RemovalPolicy.DESTROY,
        )

        # 2. Cognito User Pool Client
        # アプリケーションがユーザープールにアクセスするためのクライアント
        self.user_pool_client = cognito.UserPoolClient(
            self, "FactifyUserPoolClient",
            user_pool=self.user_pool,
            user_pool_client_name="factify-web-client",
            # OAuth設定
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE
                ],
                callback_urls=[
                    "http://localhost:3000/auth/callback",  # 開発環境用
                    "https://your-domain.com/auth/callback"  # 本番環境用（実際のドメインに変更）
                ],
                logout_urls=[
                    "http://localhost:3000/",  # 開発環境用
                    "https://your-domain.com/"  # 本番環境用（実際のドメインに変更）
                ]
            ),
            # 認証フロー設定
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                custom=True
            ),
            # トークンの有効期限
            access_token_validity=Duration.hours(24),
            id_token_validity=Duration.hours(24),
            refresh_token_validity=Duration.days(30),
            # セキュリティ設定
            prevent_user_existence_errors=True,
        )

        # 3. Cognito Identity Pool
        # 認証されたユーザーに一時的なAWS認証情報を提供
        self.identity_pool = cognito.CfnIdentityPool(
            self, "FactifyIdentityPool",
            identity_pool_name="factify_identity_pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name
                )
            ]
        )

        # 4. IAM Role for QuickSight Users
        # QuickSightにアクセスするための認証済みユーザー用ロール
        self.quicksight_user_role = iam.Role(
            self, "QuickSightUserRole",
            role_name="FactifyQuickSightUserRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                }
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonQuickSightReadOnlyAccess")
            ]
        )

        # 5. IAM Role for Unauthenticated Users (基本的には使用しない)
        self.unauthenticated_role = iam.Role(
            self, "UnauthenticatedRole",
            role_name="FactifyUnauthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    }
                }
            )
        )

        # 6. Identity Pool Role Attachment
        cognito.CfnIdentityPoolRoleAttachment(
            self, "IdentityPoolRoleAttachment",
            identity_pool_id=self.identity_pool.ref,
            roles={
                "authenticated": self.quicksight_user_role.role_arn,
                "unauthenticated": self.unauthenticated_role.role_arn
            }
        )

        # 7. QuickSight Data Source (DynamoDB)
        # QuickSightがDynamoDBに接続するためのデータソース
        # 注意: QuickSightのリソースはCfnリソースを使用する必要があります
        
        # QuickSight用のサービスロール
        self.quicksight_service_role = iam.Role(
            self, "QuickSightServiceRole",
            role_name="aws-quicksight-service-role-v0",
            assumed_by=iam.ServicePrincipal("quicksight.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSQuickSightDynamoDBAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSQuickSightS3ConsumerReadWriteAccess")
            ]
        )

        # 8. Outputs
        CfnOutput(
            self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )

        CfnOutput(
            self, "UserPoolClientId", 
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID"
        )

        CfnOutput(
            self, "IdentityPoolId",
            value=self.identity_pool.ref,
            description="Cognito Identity Pool ID"
        )

        CfnOutput(
            self, "UserPoolDomain",
            value=f"https://{self.user_pool.user_pool_id}.auth.{self.region}.amazoncognito.com",
            description="Cognito User Pool Domain"
        )

    def create_quicksight_account(self, admin_email: str) -> None:
        """
        QuickSight アカウントを作成する（手動実行が必要）
        このメソッドは、スタックデプロイ後に手動で実行する必要があります。
        """
        # QuickSight Account Registration (これは手動で実行する必要があります)
        # aws quicksight register-user コマンドまたはコンソールから実行
        
        CfnOutput(
            self, "QuickSightSetupInstructions",
            value=f"QuickSightアカウントを手動で作成してください。管理者メール: {admin_email}",
            description="QuickSight setup instructions"
        )
