#!/bin/bash
set -e

# お嬢様デプロイスクリプトですわ～！

# 1. API/インフラのCDKデプロイ（最初にAPI Gatewayを作成）
cd ./infra
echo "🌸 CDKデプロイを実行いたしますわ～！"
cdk deploy --all

# 2. API Gateway URLを取得
echo "🌸 API Gateway URLを取得いたしますわ～！"
API_GATEWAY_URL=$(aws cloudformation describe-stacks \
  --stack-name FastapiFargateCdkStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

if [ -z "$API_GATEWAY_URL" ]; then
  echo "❌ API Gateway URLの取得に失敗いたしましたわ！"
  exit 1
fi

echo "🌸 取得したAPI Gateway URL: $API_GATEWAY_URL"

# 3. .env.productionを更新
cd ../webapp
echo "🌸 .env.productionを更新いたしますわ～！"
cat > .env.production << EOF
REACT_APP_API_ENDPOINT=$API_GATEWAY_URL
EOF

# 4. webappビルド
echo "🌸 webappのビルド開始ですわ～！"
npm install
npm run build

# 5. S3へアップロード
S3_BUCKET="factify-webapp-471112951833-ap-northeast-1"
echo "🌸 S3へアップロードいたしますわ～！"
aws s3 sync dist/ s3://$S3_BUCKET --delete

# 6. CloudFrontキャッシュ無効化
CLOUDFRONT_ID="E3ERDWFXSIG6CL"
echo "🌸 CloudFrontキャッシュを無効化いたしますわ～！"
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths '/*'

echo "✨ デプロイ完了ですわ！最高のwebappを世界に解き放ちましたわ～！"
echo "🌸 API Gateway URL: $API_GATEWAY_URL"
