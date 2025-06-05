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
    print(f"[DEBUG] Starting token verification for token: {token[:20]}...")
    
    try:
        # JWTヘッダーを取得
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        print(f"[DEBUG] Token header kid: {kid}")
        
        # 公開鍵を取得
        jwks = get_cognito_public_keys()
        key = None
        for jwk in jwks["keys"]:
            if jwk["kid"] == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            print(f"[DEBUG] No matching key found for kid: {kid}")
            raise HTTPException(status_code=401, detail="Invalid token key")
        
        print(f"[DEBUG] Found matching key, verifying token...")
        
        # トークンタイプを確認してaudienceを決定
        # AccessTokenの場合はaudienceを検証しない（client_idクレームで代替）
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        token_use = unverified_payload.get("token_use")
        
        print(f"[DEBUG] Token type: {token_use}")
        
        if token_use == "access":
            # AccessTokenの場合はaudienceチェックを無効化
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},  # audienceチェックを無効化
                issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
            )
            # client_idクレームを手動で検証
            if payload.get("client_id") != COGNITO_CLIENT_ID:
                print(f"[DEBUG] Invalid client_id: expected {COGNITO_CLIENT_ID}, got {payload.get('client_id')}")
                raise HTTPException(status_code=401, detail="Invalid client_id")
        elif token_use == "id":
            # IdTokenの場合は通常のaudience検証
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=COGNITO_CLIENT_ID,
                issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
            )
        else:
            print(f"[DEBUG] Unknown token_use: {token_use}")
            raise HTTPException(status_code=401, detail="Invalid token_use")
        
        print(f"[DEBUG] Token verification successful for sub: {payload.get('sub')}")
        return payload
    except jwt.ExpiredSignatureError:
        print("[DEBUG] Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"[DEBUG] Invalid token error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """現在のユーザー情報を取得（JWT検証付き）"""
    print(f"[DEBUG] get_current_user called, credentials: {credentials is not None}")
    
    if not credentials:
        print("[DEBUG] No authorization header found")
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = credentials.credentials
    print(f"[DEBUG] Token received: {token[:20]}...")
    
    # Cognito設定チェック
    if not COGNITO_USER_POOL_ID or not COGNITO_CLIENT_ID:
        print(f"[DEBUG] Cognito config missing - Pool ID: {COGNITO_USER_POOL_ID}, Client ID: {COGNITO_CLIENT_ID}")
        raise HTTPException(status_code=500, detail="Cognito configuration missing")
    
    try:
        # Cognito JWT検証
        payload = verify_cognito_token(token)
        print(f"[DEBUG] Token verification successful for user: {payload.get('cognito:username')}")
        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "username": payload.get("cognito:username"),
            "groups": payload.get("cognito:groups", [])
        }
    except Exception as e:
        print(f"[DEBUG] Token verification failed: {str(e)}")
        raise

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
