/**
 * AWS Cognito認証設定
 * 本番環境用の固定値
 */

export const COGNITO_CONFIG = {
  REGION: 'ap-northeast-1',
  USER_POOL_ID: 'ap-northeast-1_GVKrqAF1Z',
  USER_POOL_CLIENT_ID: '4206891n3vq05t63etnh99qcsr',
} as const;

// タイプ安全性のための型定義
export type CognitoConfig = typeof COGNITO_CONFIG;
