#!/bin/bash

# CDKスタックから認証情報を取得し、.env.localファイルを更新するスクリプト

echo "CDKスタックから認証情報を取得中..."

# CDKディレクトリに移動
cd /home/yotu/github/2506-hack1/factify/infra

# CDKのアウトプットを取得
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name CognitoAuthStack --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text --region ap-northeast-1)
USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks --stack-name CognitoAuthStack --query "Stacks[0].Outputs[?OutputKey=='UserPoolClientId'].OutputValue" --output text --region ap-northeast-1)

echo "User Pool ID: $USER_POOL_ID"
echo "User Pool Client ID: $USER_POOL_CLIENT_ID"

# webappディレクトリに戻る
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
cd ../api
cat > .env << EOF
COGNITO_REGION=ap-northeast-1
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$USER_POOL_CLIENT_ID
EOF

echo ".env.local と api/.env ファイルが更新されました"
echo "フロントエンドを再起動してください: npm run dev"
echo "APIを再起動してください: cd api && python main.py"
