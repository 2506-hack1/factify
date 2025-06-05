#!/bin/bash

# CDKスタックから認証情報を取得し、環境ファイルを更新するスクリプト

echo "🔄 CDKスタックから認証情報を取得中..."

# CDKディレクトリに移動
cd /home/yotu/github/2506-hack1/factify/infra

# CDKのアウトプットを取得
echo "   Cognitoスタックの情報を取得..."
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name CognitoAuthStack --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text --region ap-northeast-1)
USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks --stack-name CognitoAuthStack --query "Stacks[0].Outputs[?OutputKey=='UserPoolClientId'].OutputValue" --output text --region ap-northeast-1)

# 取得確認
if [ "$USER_POOL_ID" = "None" ] || [ "$USER_POOL_CLIENT_ID" = "None" ] || [ -z "$USER_POOL_ID" ] || [ -z "$USER_POOL_CLIENT_ID" ]; then
    echo "❌ エラー: Cognitoの情報を取得できませんでした"
    echo "   CDKスタックがデプロイされているか確認してください"
    exit 1
fi

echo "✅ 取得完了:"
echo "   User Pool ID: $USER_POOL_ID"
echo "   User Pool Client ID: $USER_POOL_CLIENT_ID"

# webappディレクトリに移動して.env.localを更新
echo ""
echo "📝 Webapp環境変数を更新中..."
cd ../webapp

# .env.localファイルを更新
cat > .env.local << EOF
# Local development environment variables
# Auto-generated from CDK stack outputs

# Cognito設定
VITE_USER_POOL_ID=$USER_POOL_ID
VITE_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
VITE_AWS_REGION=ap-northeast-1

# API設定
VITE_API_BASE_URL=http://localhost:8000

# 開発用設定
VITE_ENV=development
EOF

# API用の.envファイルも更新
echo ""
echo "📝 API環境変数を更新中..."
cd ../api

# API用の.envファイルを作成/更新
cat > .env << EOF
# API Environment Variables
# Auto-generated from CDK stack outputs - $(date)

# Cognito Configuration
COGNITO_REGION=ap-northeast-1
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$USER_POOL_CLIENT_ID

# AWS Configuration
AWS_DEFAULT_REGION=ap-northeast-1
EOF

echo ""
echo "🎉 環境変数の更新が完了しました！"
echo "   ✅ webapp/.env.local - フロントエンド設定"
echo "   ✅ api/.env - バックエンド設定"
echo ""
echo "次のステップ:"
echo "   📱 フロントエンドを再起動: cd webapp && npm run dev"
echo "   🔧 APIを再起動: cd api && python main.py"
