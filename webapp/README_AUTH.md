# Factify WebApp - 認証機能

このWebアプリケーションにはAWS Cognitoを使用した認証機能が実装されています。

## 機能

- ✅ ユーザーサインアップ（メール確認付き）
- ✅ ユーザーサインイン
- ✅ 認証状態管理
- ✅ プライベートルート保護
- ✅ 自動ログアウト（トークン期限切れ時）
- ✅ ナビゲーション（認証状態表示）

## セットアップ

### 1. 依存関係のインストール

```bash
cd webapp
npm install
```

### 2. 環境変数の設定

CDKをデプロイした後、認証情報を取得して設定します：

```bash
# プロジェクトルートから実行
./update_env.sh
```

または手動で `.env.local` ファイルを作成：

```bash
cp .env.example .env.local
# .env.local を編集して実際の値を設定
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

## 使用方法

### 新規ユーザー登録

1. `/signup` にアクセス
2. メールアドレス、ユーザー名、パスワードを入力
3. 登録後、メールで送信される確認コードを入力
4. アカウントが有効化されます

### サインイン

1. `/signin` にアクセス
2. ユーザー名（またはメールアドレス）とパスワードを入力
3. 認証後、保護されたページにアクセス可能

### 保護されたページ

- `/upload` - 認証されたユーザーのみアクセス可能
- 未認証の場合は自動的にサインインページにリダイレクト

## 技術仕様

### 認証フロー

1. **サインアップ**: Cognito User Pool にユーザー作成
2. **メール確認**: 確認コードによるアカウント有効化
3. **サインイン**: JWT トークンの取得
4. **トークン管理**: localStorage での永続化
5. **自動認証**: アプリ起動時のトークン検証

### セキュリティ

- パスワード: 8文字以上必須
- JWT トークン: 自動期限切れ処理
- HTTPS: 本番環境で必須
- CORS: API アクセス制御

### API認証

APIクライアントは自動的に認証ヘッダーを付加：

```typescript
// 自動的に Authorization: Bearer <token> が追加される
import { api } from './services/apiClient';

const data = await api.get('/protected-endpoint');
```

## トラブルシューティング

### よくある問題

1. **Cognito設定エラー**
   - `.env.local` の設定値を確認
   - CDKスタックが正常にデプロイされているか確認

2. **メール確認が届かない**
   - スパムフォルダを確認
   - Cognitoのメール設定を確認

3. **API認証エラー**
   - トークンの有効期限を確認
   - 再ログインを試行

### デバッグ

ブラウザの開発者ツールでコンソールログとネットワークタブを確認してください。

## 環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `REACT_APP_USER_POOL_ID` | Cognito User Pool ID | `ap-northeast-1_XXXXXXXXX` |
| `REACT_APP_USER_POOL_CLIENT_ID` | User Pool Client ID | `xxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `REACT_APP_AWS_REGION` | AWS リージョン | `ap-northeast-1` |
| `REACT_APP_API_BASE_URL` | API ベース URL | `https://api.example.com` |
