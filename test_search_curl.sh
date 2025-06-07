#!/bin/bash
# API Gateway経由での検索テスト用curlコマンド集

API_ENDPOINT="https://mzm5j4xn2j.execute-api.ap-northeast-1.amazonaws.com"

echo "🔍 API Gateway経由での検索テストコマンド集ですわ～！"
echo "API Endpoint: $API_ENDPOINT"
echo

# 1. 基本的な検索テスト（認証なし）
echo "=== 1. 基本検索テスト（認証なし） ==="
echo "curl -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -d '{\"query\": \"Python\", \"max_results\": 5}' | jq ."
echo

# 2. より詳細な検索テスト
echo "=== 2. 詳細検索テスト ==="
echo "curl -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -d '{\"query\": \"AWS機械学習\", \"max_results\": 10, \"user_only\": false}' | jq ."
echo

# 3. 複数の検索語句でのテスト
echo "=== 3. 複数キーワード検索 ==="
echo "curl -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -d '{\"query\": \"データ分析 Python プログラミング\", \"max_results\": 3}' | jq ."
echo

# 4. レスポンス詳細確認用（ヘッダー含む）
echo "=== 4. レスポンス詳細確認（ヘッダー付き） ==="
echo "curl -v -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -d '{\"query\": \"OpenSearch\", \"max_results\": 2}'"
echo

# 5. CORS対応テスト（Origin ヘッダー付き）
echo "=== 5. CORS対応テスト ==="
echo "curl -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -H \"Origin: https://d2gf2wvyuful49.cloudfront.net\" \\"
echo "  -d '{\"query\": \"FastAPI\", \"max_results\": 5}' | jq ."
echo

# 6. ヘルスチェック
echo "=== 6. ヘルスチェック ==="
echo "curl -X GET \"$API_ENDPOINT/health\" | jq ."
echo

# 7. 認証ありの検索（Cognitoトークンが必要）
echo "=== 7. 認証付き検索（要トークン） ==="
echo "# まずトークンを取得してください："
echo "# TOKEN=\$(./scripts/get_token.sh)"
echo "# 次に以下のコマンドを実行："
echo "curl -X POST \"$API_ENDPOINT/search\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -H \"Accept: application/json\" \\"
echo "  -H \"Authorization: Bearer \$TOKEN\" \\"
echo "  -d '{\"query\": \"Python\", \"max_results\": 5, \"user_only\": true}' | jq ."
echo

echo "💡 使い方："
echo "1. 上記のコマンドをコピー＆ペーストして実行"
echo "2. jqが無い場合は '| jq .' の部分を削除"
echo "3. 認証付きテストの場合は先にCognitoトークンを取得"
echo "4. 各レスポンスでトランザクション記録が動作しているか確認"
echo
echo "🎯 トランザクション記録確認方法："
echo "- 検索実行後、Analyticsページで収益データを確認"
echo "- DynamoDBのaccess-logsテーブルを直接確認"
echo "- /incentive/summary エンドポイントでデータ確認"
