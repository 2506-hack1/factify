import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';
import { authService } from './authService';

export interface ApiConfig {
  baseURL: string;
  timeout: number;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(config: ApiConfig) {
    this.client = axios.create(config);
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // リクエストインターセプター：認証トークンを自動追加
    this.client.interceptors.request.use(
      (config) => {
        const token = authService.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log('Adding Authorization header with token:', token.substring(0, 20) + '...');
        } else {
          console.log('No access token found');
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // レスポンスインターセプター：401エラー時の処理
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        console.log('API Error:', error.response?.status, error.response?.data);
        
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          console.log('401 error - attempting token refresh');
          
          // authServiceのリフレッシュメソッドを呼び出し
          try {
            // 直接authServiceの内部メソッドにアクセスできないので、
            // getCurrentUserを呼び出してリフレッシュを試行
            const user = await authService.getCurrentUser();
            
            if (user) {
              // リフレッシュ成功、元のリクエストを再実行
              const newToken = authService.getAccessToken();
              if (newToken) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return this.client(originalRequest);
              }
            }
          } catch (refreshError) {
            console.log('Token refresh failed:', refreshError);
          }
          
          // リフレッシュ失敗の場合、サインアウトしてリダイレクト
          console.log('Token refresh failed - signing out and redirecting');
          await authService.signOut();
          window.location.href = '/signin';
        }
        
        return Promise.reject(error);
      }
    );
  }

  // HTTP メソッド
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch(url, data, config);
    return response.data;
  }
}

// APIクライアントのインスタンス作成
const apiConfig: ApiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: 10000,
};

export const apiClient = new ApiClient(apiConfig);

// 便利な関数をエクスポート
export const api = {
  get: apiClient.get.bind(apiClient),
  post: apiClient.post.bind(apiClient),
  put: apiClient.put.bind(apiClient),
  delete: apiClient.delete.bind(apiClient),
  patch: apiClient.patch.bind(apiClient),
};
