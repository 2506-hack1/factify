/**
 * AWS Cognito認証設定
 * 環境変数から読み込み、フォールバック値を本番環境値に設定
 */

export const COGNITO_CONFIG = {
  REGION: import.meta.env.VITE_AWS_REGION || 'ap-northeast-1',
  USER_POOL_ID: import.meta.env.VITE_USER_POOL_ID || 'ap-northeast-1_djKleJ9sI',
  USER_POOL_CLIENT_ID: import.meta.env.VITE_USER_POOL_CLIENT_ID || '7vo039n3ss61uaiieqb1toi6sq',
} as const;

// タイプ安全性のための型定義
export type CognitoConfig = typeof COGNITO_CONFIG;
