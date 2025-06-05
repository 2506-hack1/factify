import { COGNITO_CONFIG } from './cognito';

// AWS Cognito 設定（定数ファイルから読み込み）
export const cognitoConfig = {
  region: COGNITO_CONFIG.REGION,
  userPoolId: COGNITO_CONFIG.USER_POOL_ID,
  userPoolWebClientId: COGNITO_CONFIG.USER_POOL_CLIENT_ID,
};

// 認証設定（定数ベース）
export const authConfig = {
  region: cognitoConfig.region,
  userPoolId: cognitoConfig.userPoolId,
  userPoolWebClientId: cognitoConfig.userPoolWebClientId,
};
