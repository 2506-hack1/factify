import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card.tsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs.tsx';
import { Badge } from '../components/ui/Badge.tsx';
import { Button } from '../components/ui/Button.tsx';
import { api } from '../services/apiClient';
import { authService } from '../services/authService';
import './Analytics.css';

interface UserStats {
  success: boolean;
  user_id: string;
  statistics: {
    total_files: number;
    file_types: Record<string, number>;
    total_text_length: number;
    average_text_length: number;
  };
}

interface DocumentAccessDetails {
  access_count: number;
  unique_users: number;
}

interface IncentiveData {
  success: boolean;
  owner_user_id: string;
  period: string;
  total_access_count: number;
  unique_users_count: number;
  total_incentive_points: number;
  document_access_details: Record<string, DocumentAccessDetails>;
}

interface AccessLog {
  transaction_id: string;
  accessed_document_id: string;
  timestamp: string;
  search_query: string;
  search_rank: number;
  access_type: string;
}

interface UserAccessLogs {
  success: boolean;
  user_id: string;
  total_logs: number;
  access_logs: AccessLog[];
}

const Analytics: React.FC = () => {
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [incentiveData, setIncentiveData] = useState<IncentiveData | null>(null);
  const [accessLogs, setAccessLogs] = useState<UserAccessLogs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(new Date().toISOString().slice(0, 7)); // YYYY-MM

  const isAuthenticated = authService.isAuthenticated();

  const loadAnalyticsData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // 並列でデータを取得
      const [statsResponse, incentiveResponse, logsResponse] = await Promise.all([
        api.get<UserStats>('/files/user/stats'),
        api.get<IncentiveData>(`/incentive/user?period=${selectedPeriod}`),
        api.get<UserAccessLogs>('/access-logs/user')
      ]);

      setUserStats(statsResponse);
      setIncentiveData(incentiveResponse);
      setAccessLogs(logsResponse);
    } catch (err) {
      console.error('Analytics data loading error:', err);
      setError('データの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod]);

  useEffect(() => {
    if (!isAuthenticated) {
      setError('認証が必要です');
      setLoading(false);
      return;
    }

    loadAnalyticsData();
  }, [isAuthenticated, loadAnalyticsData]);

  const formatFileType = (fileType: string): string => {
    const typeMap: Record<string, string> = {
      'pdf': 'PDF',
      'docx': 'Word',
      'txt': 'テキスト',
      'html': 'HTML'
    };
    return typeMap[fileType] || fileType.toUpperCase();
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('ja-JP');
  };

  if (!isAuthenticated) {
    return (
      <div className="analytics-container">
        <Card>
          <CardContent className="text-center py-8">
            <p>アクセス分析を表示するには認証が必要です。</p>
            <Button 
              onClick={() => window.location.href = '/signin'} 
              className="mt-4"
            >
              サインイン
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading-spinner">データを読み込み中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadAnalyticsData} className="mt-4">
              再試行
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h1>📊 アクセス分析ダッシュボード</h1>
        <div className="period-selector">
          <label htmlFor="period">分析期間:</label>
          <input
            id="period"
            type="month"
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="period-input"
          />
        </div>
      </div>

      <Tabs defaultValue="overview" className="analytics-tabs">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="files">ファイル統計</TabsTrigger>
          <TabsTrigger value="revenue">💰 収益</TabsTrigger>
          <TabsTrigger value="activity">アクティビティ</TabsTrigger>
        </TabsList>

        {/* 概要タブ */}
        <TabsContent value="overview" className="overview-tab">
          <div className="overview-grid">
            <Card>
              <CardHeader>
                <CardTitle>📁 総ファイル数</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{userStats?.statistics.total_files || 0}</div>
                <p className="stat-label">アップロード済み</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>💰 今月の収益</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{incentiveData?.total_incentive_points || 0}</div>
                <p className="stat-label">ポイント獲得</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>👥 ユニークアクセス</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{incentiveData?.unique_users_count || 0}</div>
                <p className="stat-label">人がアクセス</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>📊 総アクセス数</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{incentiveData?.total_access_count || 0}</div>
                <p className="stat-label">回アクセス</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>💰 収益ポイント</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{incentiveData?.total_incentive_points || 0}</div>
                <p className="stat-label">今月の獲得ポイント</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>📊 総アクセス数</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="stat-value">{incentiveData?.total_access_count || 0}</div>
                <p className="stat-label">今月のアクセス数</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* ファイル統計タブ */}
        <TabsContent value="files" className="files-tab">
          <div className="files-stats-grid">
            <Card>
              <CardHeader>
                <CardTitle>📄 ファイル種別分布</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="file-types-list">
                  {userStats?.statistics.file_types && 
                    Object.entries(userStats.statistics.file_types).map(([type, count]) => (
                      <div key={type} className="file-type-item">
                        <Badge variant="secondary">{formatFileType(type)}</Badge>
                        <span className="file-count">{count}件</span>
                      </div>
                    ))
                  }
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>📝 テキスト統計</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-stats">
                  <div className="text-stat-item">
                    <span className="text-stat-label">総文字数:</span>
                    <span className="text-stat-value">
                      {userStats?.statistics.total_text_length?.toLocaleString() || 0}
                    </span>
                  </div>
                  <div className="text-stat-item">
                    <span className="text-stat-label">平均文字数:</span>
                    <span className="text-stat-value">
                      {userStats?.statistics.average_text_length?.toLocaleString() || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 収益タブ */}
        <TabsContent value="revenue" className="revenue-tab">
          <div className="files-stats-grid">
            <Card>
              <CardHeader>
                <CardTitle>💰 収益概要 ({selectedPeriod})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="revenue-summary">
                  <div className="revenue-overview">
                    <div className="revenue-metric">
                      <span className="revenue-label">総収益ポイント:</span>
                      <span className="revenue-value">{incentiveData?.total_incentive_points || 0} pt</span>
                    </div>
                    <div className="revenue-metric">
                      <span className="revenue-label">総アクセス数:</span>
                      <span className="revenue-value">{incentiveData?.total_access_count || 0}回</span>
                    </div>
                    <div className="revenue-metric">
                      <span className="revenue-label">ユニークユーザー:</span>
                      <span className="revenue-value">{incentiveData?.unique_users_count || 0}人</span>
                    </div>
                    <div className="revenue-metric">
                      <span className="revenue-label">平均アクセス単価:</span>
                      <span className="revenue-value">
                        {incentiveData?.total_access_count 
                          ? Math.round((incentiveData.total_incentive_points / incentiveData.total_access_count) * 100) / 100
                          : 0
                        } pt/回
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>📊 ドキュメント別収益</CardTitle>
              </CardHeader>
              <CardContent>
                {incentiveData?.document_access_details && (
                  <div className="document-revenue-list">
                    {Object.entries(incentiveData.document_access_details)
                      .sort(([,a], [,b]) => b.access_count - a.access_count)
                      .map(([docId, details]) => {
                        const revenue = details.access_count + (details.unique_users * 5);
                        return (
                          <div key={docId} className="document-revenue-item">
                            <div className="document-info">
                              <span className="document-id">{docId.slice(0, 8)}...</span>
                              <div className="document-stats">
                                <span>アクセス: {details.access_count}回</span>
                                <span>ユーザー: {details.unique_users}人</span>
                              </div>
                            </div>
                            <div className="document-revenue">
                              <span className="revenue-amount">{revenue} pt</span>
                              <div className="revenue-breakdown">
                                <small>基本: {details.access_count}pt + ボーナス: {details.unique_users * 5}pt</small>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                )}
                {(!incentiveData?.document_access_details || Object.keys(incentiveData.document_access_details).length === 0) && (
                  <p className="no-revenue">まだ収益がありません。ドキュメントをアップロードして他のユーザーに参照してもらいましょう！</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* アクティビティタブ */}
        <TabsContent value="activity" className="activity-tab">
          <Card>
            <CardHeader>
              <CardTitle>🕒 最近のアクティビティ</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="activity-list">
                {accessLogs?.access_logs?.slice(0, 20).map((log) => (
                  <div key={log.transaction_id} className="activity-item">
                    <div className="activity-info">
                      <span className="activity-query">"{log.search_query}"</span>
                      <span className="activity-type">{log.access_type}</span>
                    </div>
                    <div className="activity-meta">
                      <span className="activity-rank">#{log.search_rank}</span>
                      <span className="activity-time">{formatDate(log.timestamp)}</span>
                    </div>
                  </div>
                ))}
                {(!accessLogs?.access_logs || accessLogs.access_logs.length === 0) && (
                  <p className="no-activity">まだアクティビティがありません</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;
