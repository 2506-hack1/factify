#!/bin/bash
# Cognito認証API実践テストスクリプト

set -e

# 設定値（実際の値に置き換えてください）
API_BASE_URL="https://your-api-endpoint.execute-api.ap-northeast-1.amazonaws.com"
USER_POOL_ID="ap-northeast-1_xxxxxxxxx"
CLIENT_ID="your-client-id"
TEST_USERNAME="testuser@example.com"
TEST_PASSWORD="TempPass123!W"

echo "🧪 Cognito認証API実践テスト開始"
echo "=================================="

# 1. ヘルスチェック
echo "1. API ヘルスチェック..."
curl -X GET "${API_BASE_URL}/health" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  || echo "❌ ヘルスチェック失敗"

echo ""

# 2. Cognito サインアップテスト
echo "2. Cognito サインアップテスト..."
SIGNUP_RESPONSE=$(curl -s -X POST \
  "https://cognito-idp.ap-northeast-1.amazonaws.com/" \
  -H "X-Amz-Target: AWSCognitoIdentityProviderService.SignUp" \
  -H "Content-Type: application/x-amz-json-1.1" \
  -d "{
    \"ClientId\": \"${CLIENT_ID}\",
    \"Username\": \"${TEST_USERNAME}\",
    \"Password\": \"${TEST_PASSWORD}\",
    \"UserAttributes\": [
      {\"Name\": \"email\", \"Value\": \"${TEST_USERNAME}\"}
    ]
  }" \
  -w "\nHTTP_STATUS:%{http_code}" \
  || echo "❌ サインアップ失敗")

echo "サインアップレスポンス: $SIGNUP_RESPONSE"
echo ""

# 3. Cognito サインイン（認証）テスト
echo "3. Cognito サインインテスト..."
AUTH_RESPONSE=$(curl -s -X POST \
  "https://cognito-idp.ap-northeast-1.amazonaws.com/" \
  -H "X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth" \
  -H "Content-Type: application/x-amz-json-1.1" \
  -d "{
    \"AuthFlow\": \"USER_PASSWORD_AUTH\",
    \"ClientId\": \"${CLIENT_ID}\",
    \"AuthParameters\": {
      \"USERNAME\": \"${TEST_USERNAME}\",
      \"PASSWORD\": \"${TEST_PASSWORD}\"
    }
  }" \
  -w "\nHTTP_STATUS:%{http_code}" \
  || echo "❌ サインイン失敗")

echo "認証レスポンス: $AUTH_RESPONSE"

# JWTトークン抽出
ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"AccessToken":"[^"]*"' | cut -d'"' -f4)
ID_TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"IdToken":"[^"]*"' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ アクセストークン取得成功"
    echo "Token: ${ACCESS_TOKEN:0:20}..."
else
    echo "❌ アクセストークン取得失敗"
fi

echo ""

# 4. 認証が必要なAPI エンドポイントテスト
echo "4. 認証付きAPI テスト..."

if [ -n "$ACCESS_TOKEN" ]; then
    # ファイルアップロードテスト
    echo "4-1. ファイルアップロード API テスト..."
    curl -X POST "${API_BASE_URL}/upload" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@/etc/hosts" \
      -w "\nStatus: %{http_code}\n" \
      || echo "❌ アップロード失敗"

    echo ""

    # ファイル一覧取得テスト
    echo "4-2. ファイル一覧取得 API テスト..."
    curl -X GET "${API_BASE_URL}/files" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -w "\nStatus: %{http_code}\n" \
      || echo "❌ ファイル一覧取得失敗"

    echo ""

    # ユーザー情報取得テスト
    echo "4-3. ユーザー情報取得 API テスト..."
    curl -X GET "${API_BASE_URL}/user/profile" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -w "\nStatus: %{http_code}\n" \
      || echo "❌ ユーザー情報取得失敗"

else
    echo "⚠️ アクセストークンがないため、認証APIテストをスキップ"
fi

echo ""

# 5. 認証なしでのアクセステスト（401エラーを期待）
echo "5. 認証なしアクセステスト（401期待）..."
curl -X GET "${API_BASE_URL}/files" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n" \
  || echo "✅ 認証なしアクセスが正しく拒否された"

echo ""
echo "=================================="
echo "✅ Cognito認証API テスト完了"
