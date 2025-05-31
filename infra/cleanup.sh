#!/bin/bash
# filepath: /home/yotu/github/2506-hack1/factify/infra/cleanup.sh

echo "FastapiFargateCdkStack関連の残存リソースを検索して削除します..."

# リージョン設定
REGION="ap-northeast-1"

# プロジェクト名に基づくリソースの接頭辞（適宜変更してください）
PREFIX="FastapiFargateCdk"

echo "ECRリポジトリを削除中..."
aws ecr delete-repository --repository-name fastapi-app --force --region $REGION || echo "fastapi-app リポジトリが見つからないか、削除に失敗しました"

# その他のECRリポジトリの削除
echo "その他のECRリポジトリを確認中..."
REPOS=$(aws ecr describe-repositories --region $REGION --query "repositories[?contains(repositoryName, '$PREFIX') || contains(repositoryName, 'fastapi')].repositoryName" --output text)
if [ ! -z "$REPOS" ]; then
  echo "以下のECRリポジトリを削除します: $REPOS"
  for REPO in $REPOS; do
    # リポジトリ内のイメージを強制削除
    aws ecr delete-repository --repository-name $REPO --force --region $REGION
    echo "$REPO を削除しました"
  done
else
  echo "削除対象のECRリポジトリは見つかりませんでした"
fi

# CloudWatchロググループの削除
echo "CloudWatchロググループを確認中..."
LOG_GROUPS=$(aws logs describe-log-groups --region $REGION --query "logGroups[?contains(logGroupName, '$PREFIX') || contains(logGroupName, 'fastapi') || contains(logGroupName, '/aws/ecs/')].logGroupName" --output text)
if [ ! -z "$LOG_GROUPS" ]; then
  echo "以下のCloudWatchロググループを削除します: $LOG_GROUPS"
  for LOG_GROUP in $LOG_GROUPS; do
    aws logs delete-log-group --log-group-name $LOG_GROUP --region $REGION
    echo "$LOG_GROUP を削除しました"
  done
else
  echo "削除対象のCloudWatchロググループは見つかりませんでした"
fi

# ECSサービスの削除（クラスターも削除）
echo "ECSクラスターを確認中..."
CLUSTERS=$(aws ecs list-clusters --region $REGION --query "clusterArns[?contains(@, '$PREFIX') || contains(@, 'fastapi')]" --output text)
if [ ! -z "$CLUSTERS" ]; then
  echo "以下のECSクラスターを削除します: $CLUSTERS"
  for CLUSTER in $CLUSTERS; do
    # クラスター内のサービスを取得
    SERVICES=$(aws ecs list-services --cluster $CLUSTER --region $REGION --query "serviceArns[]" --output text)
    
    # サービスを削除
    for SERVICE in $SERVICES; do
      echo "サービス $SERVICE を削除中..."
      aws ecs update-service --cluster $CLUSTER --service $SERVICE --desired-count 0 --region $REGION
      aws ecs delete-service --cluster $CLUSTER --service $SERVICE --force --region $REGION
    done
    
    # クラスターを削除
    aws ecs delete-cluster --cluster $CLUSTER --region $REGION
    echo "$CLUSTER を削除しました"
  done
else
  echo "削除対象のECSクラスターは見つかりませんでした"
fi

# IAMロールの削除
echo "IAMロールを確認中..."
ROLES=$(aws iam list-roles --query "Roles[?contains(RoleName, '$PREFIX') || contains(RoleName, 'FastApi') || contains(RoleName, 'fastapi')].RoleName" --output text)
if [ ! -z "$ROLES" ]; then
  echo "以下のIAMロールを削除します: $ROLES"
  for ROLE in $ROLES; do
    # ロールにアタッチされたポリシーを取得して削除
    POLICIES=$(aws iam list-attached-role-policies --role-name $ROLE --query "AttachedPolicies[].PolicyArn" --output text)
    for POLICY in $POLICIES; do
      aws iam detach-role-policy --role-name $ROLE --policy-arn $POLICY
    done
    
    # インラインポリシーを削除
    INLINE_POLICIES=$(aws iam list-role-policies --role-name $ROLE --query "PolicyNames[]" --output text)
    for POLICY in $INLINE_POLICIES; do
      aws iam delete-role-policy --role-name $ROLE --policy-name $POLICY
    done
    
    # ロールを削除
    aws iam delete-role --role-name $ROLE
    echo "$ROLE を削除しました"
  done
else
  echo "削除対象のIAMロールは見つかりませんでした"
fi

echo "クリーンアップ完了！"

# 後片付けチェック
echo "残っているリソースをチェック中..."
echo "ECRリポジトリ:"
aws ecr describe-repositories --region $REGION --query "repositories[?contains(repositoryName, 'fastapi')].repositoryName" --output text

echo "CloudFormationスタック:"
aws cloudformation list-stacks --region $REGION --query "StackSummaries[?contains(StackName, 'FastapiFargateCdk')].StackName" --output text