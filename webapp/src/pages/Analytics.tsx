import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card.tsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs.tsx';
import { Badge } from '../components/ui/Badge.tsx';
import { Button } from '../components/ui/Button.tsx';
import { useAuth } from '../hooks/useAuth';
import { useAnalyticsData, type AccessLog } from '../hooks/useSWR';
import './Analytics.css';

const Analytics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState(new Date().toISOString().slice(0, 7)); // YYYY-MM
  
  // useAuthフックから認証情報を取得
  const { isAuthenticated, loading: authLoading } = useAuth();
  
  // SWRを使ってデータを取得
  const {
    userStats,
    incentiveData,
    accessLogs,
    weeklyActivity,
    isLoading: dataLoading,
    error,
  } = useAnalyticsData(selectedPeriod, isAuthenticated);

  console.log('🎯 Analytics render:', {
    isAuthenticated,
    authLoading,
    dataLoading,
    hasError: !!error,
    selectedPeriod,
    hasWeeklyActivity: !!weeklyActivity,
  });

  // 手動再読み込み関数（SWRのmutateを使用可能）
  const handleRetry = () => {
    console.log('🔄 Manual retry requested');
    window.location.reload(); // シンプルにページリロード
  };

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

  if (authLoading || dataLoading) {
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
            <p className="text-red-600">データの読み込みに失敗しました: {error.message || error}</p>
            <Button onClick={handleRetry} className="mt-4">
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
          <TabsTrigger value="incentives">インセンティブ</TabsTrigger>
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
                <CardTitle>🎯 今月のインセンティブ</CardTitle>
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

        {/* インセンティブタブ */}
        <TabsContent value="incentives" className="incentives-tab">
          <Card>
            <CardHeader>
              <CardTitle>🎁 インセンティブ詳細 ({selectedPeriod})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="incentive-summary">
                <div className="incentive-overview">
                  <div className="incentive-metric">
                    <span className="incentive-label">基本ポイント:</span>
                    <span className="incentive-value">{incentiveData?.total_access_count || 0} pt</span>
                  </div>
                  <div className="incentive-metric">
                    <span className="incentive-label">ユニークユーザーボーナス:</span>
                    <span className="incentive-value">{(incentiveData?.unique_users_count || 0) * 5} pt</span>
                  </div>
                  <div className="incentive-metric total">
                    <span className="incentive-label">合計:</span>
                    <span className="incentive-value">{incentiveData?.total_incentive_points || 0} pt</span>
                  </div>
                </div>

                {incentiveData?.document_access_details && (
                  <div className="document-details">
                    <h4>ドキュメント別詳細</h4>
                    <div className="document-list">
                      {Object.entries(incentiveData.document_access_details).map(([docId, details]) => (
                        <div key={docId} className="document-item">
                          <div className="document-id">{docId.slice(0, 8)}...</div>
                          <div className="document-stats">
                            <span>アクセス: {details.access_count}回</span>
                            <span>ユーザー: {details.unique_users}人</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* アクティビティタブ */}
        <TabsContent value="activity" className="activity-tab">
          <Card>
            <CardHeader>
              <CardTitle>🕒 最近のアクティビティ</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="activity-list">
                {accessLogs?.access_logs?.slice(0, 20).map((log: AccessLog) => (
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
