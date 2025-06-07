#!/bin/bash
# Cognitoアクセストークン取得ヘルパースクリプト

USER_POOL_ID=ap-northeast-1_GVKrqAF1Z
CLIENT_ID=7vo039n3ss61uaiieqb1toi6sq
REGION=ap-northeast-1

# ユーザー情報の入力
read -p "ユーザー名（メールアドレス）: " USERNAME
read -s -p "パスワード: " PASSWORD
echo ""

echo "🔐 Cognitoアクセストークン取得中..."

# Cognito認証リクエスト
AUTH_RESPONSE=$(curl -s -X POST \
  "https://cognito-idp.${REGION}.amazonaws.com/" \
  -H "X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth" \
  -H "Content-Type: application/x-amz-json-1.1" \
  -d "{
    \"AuthFlow\": \"USER_PASSWORD_AUTH\",
    \"ClientId\": \"${CLIENT_ID}\",
    \"AuthParameters\": {
      \"USERNAME\": \"${USERNAME}\",
      \"PASSWORD\": \"${PASSWORD}\"
    }
  }")

# アクセストークンを抽出
ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"AccessToken":"[^"]*"' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    echo "✅ アクセストークン取得成功!"
    echo ""
    echo "以下のトークンをコピーしてAPIテストで使用してください:"
    echo "=================================================="
    echo "$ACCESS_TOKEN"
    echo "=================================================="
    echo ""
    echo "🔍 Search APIテストの実行例:"
    echo "cd /home/yotu/github/2506-hack1/factify/api/debug"
    echo "python3 test_auth_api.py --token \"$ACCESS_TOKEN\" search \"検索キーワード\""
    echo ""
    echo "📁 ユーザーファイル一覧取得の実行例:"
    echo "python3 test_auth_api.py --token \"$ACCESS_TOKEN\" files"
else
    echo "❌ アクセストークン取得失敗"
    echo "認証レスポンス: $AUTH_RESPONSE"
    echo ""
    echo "確認事項:"
    echo "- ユーザー名とパスワードが正しいか"
    echo "- ユーザーアカウントが確認済みか"
    echo "- Cognitoの設定値が正しいか"
fi
