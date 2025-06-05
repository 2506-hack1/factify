import {
  CognitoIdentityProviderClient,
  SignUpCommand,
  ConfirmSignUpCommand,
  InitiateAuthCommand,
  GetUserCommand,
  GlobalSignOutCommand,
} from '@aws-sdk/client-cognito-identity-provider';
import { authConfig } from '../config/auth';

export interface User {
  username: string;
  email: string;
  attributes: Record<string, string>;
}

export interface AuthTokens {
  accessToken: string;
  idToken: string;
  refreshToken: string;
}

class AuthService {
  private client: CognitoIdentityProviderClient;

  constructor() {
    this.client = new CognitoIdentityProviderClient({
      region: authConfig.region,
    });
  }

  // サインアップ
  async signUp(email: string, password: string): Promise<void> {
    const command = new SignUpCommand({
      ClientId: authConfig.userPoolWebClientId,
      Username: email, // Cognitoの設定に合わせてメールアドレスをユーザー名として使用
      Password: password,
      UserAttributes: [
        {
          Name: 'email',
          Value: email,
        },
      ],
    });

    try {
      await this.client.send(command);
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  }

  // メール確認
  async confirmSignUp(username: string, confirmationCode: string): Promise<void> {
    const command = new ConfirmSignUpCommand({
      ClientId: authConfig.userPoolWebClientId,
      Username: username,
      ConfirmationCode: confirmationCode,
    });

    try {
      await this.client.send(command);
    } catch (error) {
      console.error('Confirm sign up error:', error);
      throw error;
    }
  }

  // サインイン
  async signIn(username: string, password: string): Promise<AuthTokens> {
    const command = new InitiateAuthCommand({
      ClientId: authConfig.userPoolWebClientId,
      AuthFlow: 'USER_PASSWORD_AUTH', // パスワード認証を使用
      AuthParameters: {
        USERNAME: username,
        PASSWORD: password,
      },
    });

    try {
      const response = await this.client.send(command);
      
      if (response.AuthenticationResult) {
        const tokens: AuthTokens = {
          accessToken: response.AuthenticationResult.AccessToken!,
          idToken: response.AuthenticationResult.IdToken!,
          refreshToken: response.AuthenticationResult.RefreshToken!,
        };
        
        // トークンをローカルストレージに保存
        this.storeTokens(tokens);
        return tokens;
      } else {
        throw new Error('Authentication failed');
      }
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  }

  // 現在のユーザー情報を取得
  async getCurrentUser(): Promise<User | null> {
    const tokens = this.getStoredTokens();
    if (!tokens) return null;

    const command = new GetUserCommand({
      AccessToken: tokens.accessToken,
    });

    try {
      const response = await this.client.send(command);
      
      const attributes: Record<string, string> = {};
      response.UserAttributes?.forEach(attr => {
        if (attr.Name && attr.Value) {
          attributes[attr.Name] = attr.Value;
        }
      });

      return {
        username: response.Username!,
        email: attributes.email || '',
        attributes,
      };
    } catch (error) {
      console.error('Get current user error:', error);
      // トークンが無効な場合はクリア
      this.clearTokens();
      return null;
    }
  }

  // サインアウト
  async signOut(): Promise<void> {
    const tokens = this.getStoredTokens();
    if (tokens) {
      const command = new GlobalSignOutCommand({
        AccessToken: tokens.accessToken,
      });

      try {
        await this.client.send(command);
      } catch (error) {
        console.error('Sign out error:', error);
      }
    }
    
    this.clearTokens();
  }

  // トークン管理
  private storeTokens(tokens: AuthTokens): void {
    localStorage.setItem('authTokens', JSON.stringify(tokens));
  }

  private getStoredTokens(): AuthTokens | null {
    const stored = localStorage.getItem('authTokens');
    return stored ? JSON.parse(stored) : null;
  }

  private clearTokens(): void {
    localStorage.removeItem('authTokens');
  }

  // 認証状態確認
  isAuthenticated(): boolean {
    const tokens = this.getStoredTokens();
    return !!tokens?.accessToken;
  }

  // アクセストークン取得
  getAccessToken(): string | null {
    const tokens = this.getStoredTokens();
    return tokens?.accessToken || null;
  }
}

export const authService = new AuthService();
