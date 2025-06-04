import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 環境変数（開発用デフォルト値付き）
COGNITO_REGION = os.getenv("COGNITO_REGION", "ap-northeast-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "ap-northeast-1_XXXXXXXXX")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "XXXXXXXXXXXXXXXXXXXXXXXXXX")

# デバッグモード
DEBUG_MODE = os.getenv("AUTH_DEBUG_MODE", "true").lower() == "true"

security = HTTPBearer(auto_error=False)

async def get_current_user_mock(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """
    開発用：モック認証（実際のJWT検証は次のステップで実装）
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = credentials.credentials
    
    # 開発用：簡単なトークンチェック
    if token == "dev-token":
        return {
            "user_id": "dev-user-123",
            "email": "dev@example.com",
            "username": "devuser",
            "groups": ["user"]
        }
    elif token == "admin-token":
        return {
            "user_id": "admin-user-456",
            "email": "admin@example.com", 
            "username": "adminuser",
            "groups": ["admin", "user"]
        }
    
    raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    デバッグ用：認証が任意のバージョン
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user_mock(credentials)
    except HTTPException:
        return None

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user_mock)) -> Dict[str, Any]:
    """管理者権限を要求"""
    if "admin" not in current_user.get("groups", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
