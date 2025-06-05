// AWS Cognito 設定
export const cognitoConfig = {
  region: 'ap-northeast-1',
  userPoolId: import.meta.env.VITE_USER_POOL_ID || '',
  userPoolWebClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
};

// 開発時のデフォルト値（実際の値は環境変数から設定）
export const devConfig = {
  region: 'ap-northeast-1',
  // CDKデプロイ後にこれらの値を更新してください
  userPoolId: 'ap-northeast-1_XXXXXXXXX',
  userPoolWebClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx',
};

// 環境変数が設定されていない場合は開発用設定を使用
export const authConfig = {
  region: cognitoConfig.region,
  userPoolId: cognitoConfig.userPoolId || devConfig.userPoolId,
  userPoolWebClientId: cognitoConfig.userPoolWebClientId || devConfig.userPoolWebClientId,
};
