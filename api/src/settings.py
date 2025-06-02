"""
環境変数設定とアプリケーション設定
"""
import os
from typing import Optional

class Settings:
    """アプリケーション設定クラス"""
    
    # AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")
  
    # Cognito
    COGNITO_USER_POOL_ID: Optional[str] = os.getenv("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: Optional[str] = os.getenv("COGNITO_CLIENT_ID")
    COGNITO_IDENTITY_POOL_ID: Optional[str] = os.getenv("COGNITO_IDENTITY_POOL_ID")
    
    # S3
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    
    # DynamoDB
    DYNAMODB_TABLE_NAME: Optional[str] = os.getenv("DYNAMODB_TABLE_NAME", "FileMetadata")
    
    # QuickSight
    QUICKSIGHT_ACCOUNT_ID: Optional[str] = os.getenv("QUICKSIGHT_ACCOUNT_ID")
    QUICKSIGHT_REGION: str = os.getenv("QUICKSIGHT_REGION", "ap-northeast-1")
    
    # FastAPI
    API_TITLE: str = "Factify API"
    API_DESCRIPTION: str = "ファイルアップロードと認証システム"
    API_VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",  # React開発サーバー
        "http://localhost:3001",  # 予備ポート
    ]
    
    # Security
    JWT_ALGORITHM: str = "RS256"
    JWT_VERIFY_SIGNATURE: bool = True
    JWT_VERIFY_AUD: bool = True
    JWT_VERIFY_ISS: bool = True
    JWT_VERIFY_EXP: bool = True
    
    @property
    def cognito_issuer(self) -> Optional[str]:
        """Cognito IssuerのURLを生成"""
        if self.COGNITO_USER_POOL_ID:
            return f"https://cognito-idp.{self.AWS_REGION}.amazonaws.com/{self.COGNITO_USER_POOL_ID}"
        return None
    
    @property
    def cognito_jwks_url(self) -> Optional[str]:
        """Cognito JWKS URLを生成"""
        if self.cognito_issuer:
            return f"{self.cognito_issuer}/.well-known/jwks.json"
        return None
    
    def validate_required_settings(self) -> bool:
        """必須設定のバリデーション"""
        required_vars = [
            "COGNITO_USER_POOL_ID",
            "COGNITO_CLIENT_ID",
            "S3_BUCKET_NAME"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

# グローバル設定インスタンス
settings = Settings()

# 起動時設定チェック
if __name__ == "__main__":
    print("=== Factify API Settings ===")
    print(f"AWS Region: {settings.AWS_REGION}")
    print(f"Cognito User Pool ID: {settings.COGNITO_USER_POOL_ID}")
    print(f"Cognito Client ID: {settings.COGNITO_CLIENT_ID}")
    print(f"S3 Bucket: {settings.S3_BUCKET_NAME}")
    print(f"DynamoDB Table: {settings.DYNAMODB_TABLE_NAME}")
    print(f"Settings Valid: {settings.validate_required_settings()}")
