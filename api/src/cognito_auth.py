"""
Cognito JWT認証ヘルパー関数
FastAPIアプリケーションでCognito認証を利用するためのユーティリティ
"""

import json
import jwt
import requests
from functools import wraps
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .settings import settings


class CognitoJWTAuth:
    """Cognito JWT認証クラス"""
    
    def __init__(self, 
                 user_pool_id: str, 
                 client_id: str, 
                 region: str = "ap-northeast-1"):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"
        self._jwks = None
        
    def get_jwks(self) -> Dict[str, Any]:
        """JWKSを取得（キャッシュ付き）"""
        if self._jwks is None:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self._jwks = response.json()
        return self._jwks
    
    def get_public_key(self, token_header: Dict[str, Any]) -> str:
        """JWTトークンヘッダーから公開鍵を取得"""
        kid = token_header.get('kid')
        if not kid:
            raise HTTPException(status_code=401, detail="Token header missing 'kid'")
        
        jwks = self.get_jwks()
        for key in jwks['keys']:
            if key['kid'] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        
        raise HTTPException(status_code=401, detail="Public key not found")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """JWTトークンを検証してペイロードを返す"""
        try:
            # ヘッダーを取得
            header = jwt.get_unverified_header(token)
            
            # 公開鍵を取得
            public_key = self.get_public_key(header)
            
            # トークンを検証
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer=self.issuer,
                audience=self.client_id,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True
                }
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


# グローバル認証インスタンス
cognito_auth = CognitoJWTAuth(
    user_pool_id=settings.COGNITO_USER_POOL_ID or "",
    client_id=settings.COGNITO_CLIENT_ID or "",
    region=settings.AWS_REGION
)

# HTTPBearer スキーム
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    現在のユーザー情報を取得する依存関数
    FastAPIのDependsで使用
    """
    token = credentials.credentials
    user_info = cognito_auth.verify_token(token)
    
    # ユーザー情報を整理
    return {
        "user_id": user_info.get("sub"),
        "username": user_info.get("cognito:username"),
        "email": user_info.get("email"),
        "email_verified": user_info.get("email_verified"),
        "groups": user_info.get("cognito:groups", []),
        "token_use": user_info.get("token_use"),
        "auth_time": user_info.get("auth_time"),
        "exp": user_info.get("exp")
    }


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    オプショナルなユーザー情報を取得（認証が必須でないエンドポイント用）
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        user_info = cognito_auth.verify_token(token)
        return {
            "user_id": user_info.get("sub"),
            "username": user_info.get("cognito:username"),
            "email": user_info.get("email"),
            "email_verified": user_info.get("email_verified"),
            "groups": user_info.get("cognito:groups", [])
        }
    except:
        return None


def require_auth(f):
    """
    認証が必要なエンドポイント用のデコレータ
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # FastAPIではDependsを使用するため、このデコレータは使用しない
        # 代わりにget_current_userを依存関数として使用
        return await f(*args, **kwargs)
    return decorated_function


def require_groups(allowed_groups: list):
    """
    特定のCognitoグループに属するユーザーのみアクセス可能にする依存関数を生成
    """
    async def check_groups(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_groups = current_user.get("groups", [])
        if not any(group in user_groups for group in allowed_groups):
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required groups: {allowed_groups}"
            )
        return current_user
    
    return check_groups


# 使用例関数
async def admin_only(current_user: Dict[str, Any] = Depends(require_groups(["admin"]))) -> Dict[str, Any]:
    """管理者のみアクセス可能"""
    return current_user


async def moderator_or_admin(current_user: Dict[str, Any] = Depends(require_groups(["admin", "moderator"]))) -> Dict[str, Any]:
    """管理者またはモデレーターのみアクセス可能"""
    return current_user
