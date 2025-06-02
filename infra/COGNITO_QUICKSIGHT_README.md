# Cognito & QuickSight 認証システム

このプロジェクトでは、Amazon CognitoとAmazon QuickSight Standard Editionを使用してユーザー認証とデータ可視化機能を提供します。

## アーキテクチャ概要

```
ユーザー → Cognito User Pool → Cognito Identity Pool → QuickSight
              ↓
         一時的なAWS認証情報
              ↓
         QuickSight ダッシュボード
```

## スタック構成

### 1. AuthQuickSightStack
- **Cognito User Pool**: ユーザー認証情報の管理
- **Cognito User Pool Client**: Webアプリケーション用クライアント
- **Cognito Identity Pool**: 一時的なAWS認証情報の提供
- **IAM Roles**: QuickSightアクセス用のロール

### 2. QuickSightManagementStack
- **QuickSight Account**: Standard Edition
- **Lambda Function**: QuickSight設定の自動化
- **Data Sources**: DynamoDB連携の設定

## デプロイ手順

### 1. 依存関係のインストール
```bash
cd infra
pip install -r requirements.txt
```

### 2. CDKスタックのデプロイ
```bash
# すべてのスタックをデプロイ
cdk deploy --all

# または個別にデプロイ
cdk deploy AuthQuickSightStack
cdk deploy QuickSightManagementStack
```

### 3. QuickSightアカウントの手動設定

デプロイ後、以下の手動設定が必要です：

#### 3.1 QuickSightアカウントの作成（初回のみ）
```bash
# AWS CLIを使用
aws quicksight create-account-subscription \
  --aws-account-id $(aws sts get-caller-identity --query Account --output text) \
  --account-name "factify-quicksight" \
  --notification-email "your-admin-email@example.com" \
  --edition STANDARD \
  --authentication-method IDENTITY_POOL \
  --region ap-northeast-1
```

#### 3.2 Identity Pool連携の設定
1. QuickSightコンソールにアクセス
2. **管理者設定** → **セキュリティとアクセス許可** に移動
3. **Identity Pool** を有効化
4. Cognito Identity PoolのIDを設定

## Cognito設定

### ユーザープール設定
- **サインイン方法**: メールアドレス、ユーザー名
- **パスワードポリシー**: 8文字以上、大文字・小文字・数字必須
- **セルフサインアップ**: 有効
- **メール確認**: 必須

### OAuth設定
- **許可されているOAuthフロー**: Authorization Code Grant、Implicit Grant
- **OAuth スコープ**: email、openid、profile
- **コールバックURL**: 
  - 開発環境: `http://localhost:3000/auth/callback`
  - 本番環境: `https://your-domain.com/auth/callback`

## QuickSight使用方法

### 1. データソースの設定
1. QuickSightコンソールで **新しいデータセット** を作成
2. **DynamoDB** を選択
3. 該当するテーブルを選択
4. データをインポート

### 2. ダッシュボードの作成
1. **新しい分析** を作成
2. データセットを選択
3. 可視化を追加
4. **ダッシュボードとして公開**

### 3. ユーザーアクセス管理
1. **管理者設定** → **ユーザー管理** に移動
2. Cognito Identity Poolから認証されたユーザーを招待
3. 適切な権限（閲覧者、作成者）を付与

## 環境変数

Webアプリケーションで使用する環境変数：

```env
# Cognito設定
REACT_APP_COGNITO_USER_POOL_ID=ap-northeast-1_XXXXXXXXX
REACT_APP_COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
REACT_APP_COGNITO_IDENTITY_POOL_ID=ap-northeast-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
REACT_APP_AWS_REGION=ap-northeast-1

# QuickSight設定
REACT_APP_QUICKSIGHT_URL=https://ap-northeast-1.quicksight.aws.amazon.com
```

## トラブルシューティング

### QuickSightアカウントが作成できない
- AWS アカウントでQuickSightを初めて使用する場合、手動でアカウント作成が必要
- Standard Editionの制限を確認（ユーザー数、機能制限）

### Cognito認証でエラーが発生する
- コールバックURLが正しく設定されているか確認
- OAuth設定が適切か確認
- Identity Poolの設定を確認

### QuickSightでデータが表示されない
- DynamoDBテーブルにデータが存在するか確認
- IAMロールの権限を確認
- データソースの接続設定を確認

## セキュリティ考慮事項

1. **本番環境での設定**
   - 適切なドメインでのコールバックURL設定
   - HTTPS必須
   - 本番用の管理者メールアドレス設定

2. **権限管理**
   - 最小権限の原則に従ったIAMロール設定
   - QuickSightユーザーの権限を適切に制限

3. **データ保護**
   - DynamoDBの暗号化設定
   - QuickSightでの行レベルセキュリティ検討

## コスト最適化

- **QuickSight Standard Edition**: 月額$9/ユーザー（最初のユーザーは$24）
- **Cognito**: MAU（月間アクティブユーザー）数に基づく課金
- **DynamoDB**: 読み書き容量とストレージに基づく課金

定期的に使用状況を監視し、不要なリソースを削除することを推奨します。
