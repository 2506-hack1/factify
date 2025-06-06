// SWR用のカスタムフックとfetcher関数
import useSWR, { type SWRConfiguration } from 'swr';
import { api } from '../services/apiClient';

// Analytics用の型定義
export interface UserStats {
  success: boolean;
  user_id: string;
  statistics: {
    total_files: number;
    file_types: Record<string, number>;
    total_text_length: number;
    average_text_length: number;
  };
}

export interface DocumentAccessDetails {
  access_count: number;
  unique_users: number;
}

export interface IncentiveData {
  success: boolean;
  owner_user_id: string;
  period: string;
  total_access_count: number;
  unique_users_count: number;
  total_incentive_points: number;
  document_access_details: Record<string, DocumentAccessDetails>;
}

export interface AccessLog {
  transaction_id: string;
  accessed_document_id: string;
  timestamp: string;
  search_query: string;
  search_rank: number;
  access_type: string;
}

export interface UserAccessLogs {
  success: boolean;
  user_id: string;
  total_logs: number;
  access_logs: AccessLog[];
}

export interface WeeklyActivity {
  success: boolean;
  period_days: number;
  start_date: string;
  end_date: string;
  daily_stats: Array<{
    date: string;
    unique_users: number;
    total_accesses: number;
  }>;
  total_unique_users: number;
  total_accesses: number;
}

// SWR fetcher関数
const fetcher = async (url: string) => {
  console.log('🔄 SWR fetching:', url);
  return await api.get(url);
};

// 認証が必要なエンドポイント用のカスタムフック
export const useAuthenticatedSWR = <T = unknown>(
  key: string | null, 
  config?: SWRConfiguration
) => {
  return useSWR<T>(
    key, // keyがnullの場合はリクエストしない
    fetcher,
    {
      revalidateOnFocus: false, // フォーカス時の再検証を無効
      revalidateOnReconnect: true, // 再接続時は再検証
      dedupingInterval: 5000, // 5秒間は重複リクエストを防ぐ
      errorRetryCount: 2, // エラー時の再試行回数
      ...config, // 追加設定をマージ
    }
  );
};

// Analytics専用のカスタムフック
export const useAnalyticsData = (selectedPeriod: string, isAuthenticated: boolean) => {
  // 認証されていない場合はリクエストしない
  const shouldFetch = isAuthenticated;
  
  console.log('🎯 useAnalyticsData called:', { selectedPeriod, isAuthenticated, shouldFetch });

  const {
    data: userStats,
    error: userStatsError,
    isLoading: userStatsLoading,
  } = useAuthenticatedSWR<UserStats>(
    shouldFetch ? '/files/user/stats' : null
  );

  const {
    data: incentiveData,
    error: incentiveError,
    isLoading: incentiveLoading,
  } = useAuthenticatedSWR<IncentiveData>(
    shouldFetch ? `/incentive/user?period=${selectedPeriod}` : null
  );

  const {
    data: accessLogs,
    error: accessLogsError,
    isLoading: accessLogsLoading,
  } = useAuthenticatedSWR<UserAccessLogs>(
    shouldFetch ? '/access-logs/user' : null
  );

  const {
    data: weeklyActivity,
    error: weeklyActivityError,
    isLoading: weeklyActivityLoading,
  } = useAuthenticatedSWR<WeeklyActivity>(
    shouldFetch ? '/analytics/weekly-users' : null
  );

  // 全体のローディング状態
  const isLoading = userStatsLoading || incentiveLoading || accessLogsLoading || weeklyActivityLoading;
  
  // エラーの集約
  const error = userStatsError || incentiveError || accessLogsError || weeklyActivityError;

  console.log('📊 Analytics data status:', {
    isLoading,
    hasError: !!error,
    userStats: !!userStats,
    incentiveData: !!incentiveData,
    accessLogs: !!accessLogs,
    weeklyActivity: !!weeklyActivity,
  });

  return {
    userStats,
    incentiveData,
    accessLogs,
    weeklyActivity,
    isLoading,
    error,
  };
};
