#!/bin/bash
set -e

# お嬢様デプロイスクリプトですわ～！

# 1. API/インフラのCDKデプロイ（最初にAPI Gatewayを作成）
cd ./infra
echo "🌸 CDKデプロイを実行いたしますわ～！"
cdk deploy --all

# 2. ECSタスクのパブリックIPを取得
echo "🌸 ECSタスクのパブリックIPを取得いたしますわ～！"

# ECSクラスター名とサービス名を取得
ECS_CLUSTER_NAME=$(aws cloudformation describe-stacks \
  --stack-name FastapiFargateCdkStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
  --output text)

ECS_SERVICE_NAME=$(aws cloudformation describe-stacks \
  --stack-name FastapiFargateCdkStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSServiceName`].OutputValue' \
  --output text)

# タスクARNを取得
TASK_ARN=$(aws ecs list-tasks \
  --cluster $ECS_CLUSTER_NAME \
  --service-name $ECS_SERVICE_NAME \
  --region ap-northeast-1 \
  --query 'taskArns[0]' \
  --output text)

if [ -z "$TASK_ARN" ] || [ "$TASK_ARN" = "None" ]; then
  echo "❌ ECSタスクが見つかりませんでしたわ！"
  exit 1
fi

# ネットワークインターフェースIDを取得
ENI_ID=$(aws ecs describe-tasks \
  --cluster $ECS_CLUSTER_NAME \
  --tasks $TASK_ARN \
  --region ap-northeast-1 \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text)

# パブリックIPを取得
PUBLIC_IP=$(aws ec2 describe-network-interfaces \
  --network-interface-ids $ENI_ID \
  --region ap-northeast-1 \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text)

if [ -z "$PUBLIC_IP" ] || [ "$PUBLIC_IP" = "None" ]; then
  echo "❌ パブリックIPの取得に失敗いたしましたわ！"
  exit 1
fi

API_ENDPOINT="http://$PUBLIC_IP"
echo "🌸 取得したECSタスクのパブリックIP: $PUBLIC_IP"

# 3. .env.productionを更新
cd ../webapp
echo "🌸 .env.productionを更新いたしますわ～！"
cat > .env.production << EOF
REACT_APP_API_ENDPOINT=$API_ENDPOINT
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
CLOUDFRONT_ID="E2ZAN0145JGOOO"
echo "🌸 CloudFrontキャッシュを無効化いたしますわ～！"
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths '/*'

echo "✨ デプロイ完了ですわ！最高のwebappを世界に解き放ちましたわ～！"
echo "🌸 ECS Task Public IP: $PUBLIC_IP"
echo "🌸 API Endpoint: $API_ENDPOINT"
