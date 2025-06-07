#!/bin/bash

# 🎯 API Gateway経由でFactifyの検索エンドポイントをテストするcurlコマンド集ですわ～！

API_ENDPOINT="http://18.183.115.76"

echo "🌟 Factify API Gateway 検索テスト開始ですわ～！"
echo "=============================================="

# 1. 基本的な検索テスト（認証なし）
echo "📚 1. 基本的な検索テスト（認証なし）"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "AI",
    "limit": 5
  }' | jq '.'

echo -e "\n================================\n"

# 2. 詳細な検索クエリテスト
echo "📚 2. 詳細検索テスト"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "機械学習 深層学習",
    "limit": 10
  }' | jq '.'

echo -e "\n================================\n"

# 3. 認証付き検索（ダミーJWTトークン）
echo "🔐 3. 認証付き検索テスト（ダミートークン）"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyXzEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSJ9.dummy" \
  -d '{
    "query": "データサイエンス",
    "limit": 3
  }' | jq '.'

echo -e "\n================================\n"

# 4. 空クエリテスト
echo "🤔 4. 空クエリテスト"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "",
    "limit": 5
  }' | jq '.'

echo -e "\n================================\n"

# 5. 日本語検索テスト
echo "🌸 5. 日本語検索テスト"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "人工知能の未来",
    "limit": 5
  }' | jq '.'

echo -e "\n================================\n"

# 6. 大きなリミット値テスト
echo "📈 6. 大きなリミット値テスト"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "テクノロジー",
    "limit": 50
  }' | jq '.'

echo -e "\n================================\n"

# 7. ヘルスチェック（根本エンドポイント）
echo "💊 7. ヘルスチェック"
curl -X GET "${API_ENDPOINT}/" \
  -H "Accept: application/json" | jq '.'

echo -e "\n================================\n"

# 8. CORSプリフライトテスト
echo "🌐 8. CORSプリフライトテスト"
curl -X OPTIONS "${API_ENDPOINT}/search" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -H "Origin: https://example.com" \
  -v

echo -e "\n================================\n"

# 9. エラーハンドリングテスト（不正なJSON）
echo "❌ 9. 不正なJSONテスト"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"query": "test", "limit":' | jq '.'

echo -e "\n================================\n"

# 10. レスポンスタイム測定
echo "⏱️ 10. レスポンスタイム測定"
curl -X POST "${API_ENDPOINT}/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "query": "パフォーマンステスト",
    "limit": 10
  }' \
  -w "Time: %{time_total}s\nSize: %{size_download} bytes\n" \
  -o /dev/null -s

echo -e "\n🎉 テスト完了ですわ～！"
