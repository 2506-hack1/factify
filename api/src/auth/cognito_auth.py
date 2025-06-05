import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
from ..constants.cognito import COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID

security = HTTPBearer(auto_error=False)

@lru_cache()
def get_cognito_public_keys() -> Dict[str, Any]:
    """CognitoのJWKS（JSON Web Key Set）を取得"""
    if not COGNITO_USER_POOL_ID:
        raise HTTPException(status_code=500, detail="COGNITO_USER_POOL_ID not configured")
    
    url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to get Cognito public keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Cognito public keys")

def verify_cognito_token(token: str) -> Dict[str, Any]:
    """Cognito JWTトークンを検証"""
    try:
        # JWTヘッダーを取得
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        
        # 公開鍵を取得
        jwks = get_cognito_public_keys()
        key = None
        for jwk in jwks["keys"]:
            if jwk["kid"] == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        
        # トークンを検証
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=COGNITO_CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """現在のユーザー情報を取得（JWT検証付き）"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = credentials.credentials
    
    # Cognito設定チェック
    if not COGNITO_USER_POOL_ID or not COGNITO_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Cognito configuration missing")
    
    # Cognito JWT検証
    payload = verify_cognito_token(token)
    return {
        "user_id": payload["sub"],
        "email": payload.get("email"),
        "username": payload.get("cognito:username"),
        "groups": payload.get("cognito:groups", [])
    }

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """認証オプション版：ユーザー情報を取得（認証失敗でもNoneを返す）"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """管理者権限を要求"""
    if "admin" not in current_user.get("groups", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
