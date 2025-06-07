import React, { useState } from 'react';
import './SearchDebug.css';

interface SearchResult {
  id: string;
  file_name: string;
  title: string;
  description?: string;
  formatted_text: string;
  uploaded_at: string;
  s3_key?: string;
  file_type?: string;
  extracted_metadata?: Record<string, any>;
}

interface SearchResponse {
  success: boolean;
  query: string;
  total_results: number;
  results: SearchResult[];
}

interface DebugSearchResponse {
  success: boolean;
  query: string;
  user_id: string | null;
  total_hits: number;
  returned_hits: number;
  results: Array<{
    id: string;
    score: number;
    source: {
      title: string;
      content: string;
      user_id: string;
      file_type: string;
      uploaded_at: string;
    };
  }>;
}

const SearchDebug: React.FC = () => {
  const [query, setQuery] = useState('');
  const [size, setSize] = useState(10);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [debugResults, setDebugResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchStats, setSearchStats] = useState<{
    total: number;
    responseTime: number;
    query: string;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<'main' | 'debug'>('main');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

  const performMainSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    const startTime = Date.now();

    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim(), size }),
        credentials: 'omit', // HTTPOnlyクッキーを送信しない
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const data: SearchResponse = await response.json();
      const responseTime = Date.now() - startTime;

      setResults(data.results);
      setSearchStats({
        total: data.total_results,
        responseTime,
        query: data.query,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setResults([]);
      setSearchStats(null);
    } finally {
      setLoading(false);
    }
  };

  const performDebugSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    const startTime = Date.now();

    try {
      const response = await fetch(`${API_BASE_URL}/debug/opensearch/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim(), size }),
        credentials: 'omit', // HTTPOnlyクッキーを送信しない
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const data: DebugSearchResponse = await response.json();
      const responseTime = Date.now() - startTime;

      setDebugResults(data.results);
      setSearchStats({
        total: data.total_hits,
        responseTime,
        query: data.query,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setDebugResults([]);
      setSearchStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'main') {
      performMainSearch();
    } else {
      performDebugSearch();
    }
  };

  const formatContent = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="search-debug">
      <div className="search-header">
        <h1>🔍 検索機能テスト</h1>
        <p>ドキュメント検索システムのテスト用インターフェース</p>
      </div>

      <div className="search-tabs">
        <button
          className={`tab ${activeTab === 'main' ? 'active' : ''}`}
          onClick={() => setActiveTab('main')}
        >
          標準検索
        </button>
        <button
          className={`tab ${activeTab === 'debug' ? 'active' : ''}`}
          onClick={() => setActiveTab('debug')}
        >
          詳細検索（スコア表示）
        </button>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="検索キーワードを入力してください..."
            className="search-input"
            disabled={loading}
          />
          <select
            value={size}
            onChange={(e) => setSize(Number(e.target.value))}
            className="size-select"
            disabled={loading}
          >
            <option value={5}>5件</option>
            <option value={10}>10件</option>
            <option value={20}>20件</option>
            <option value={50}>50件</option>
          </select>
          <button
            type="submit"
            className="search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? '検索中...' : '検索'}
          </button>
        </div>
      </form>

      {searchStats && (
        <div className="search-stats">
          <span className="stat">
            クエリ: <strong>"{searchStats.query}"</strong>
          </span>
          <span className="stat">
            結果: <strong>{searchStats.total}件</strong>
          </span>
          <span className="stat">
            応答時間: <strong>{searchStats.responseTime}ms</strong>
          </span>
          <span className="stat">
            検索方法: <strong>{activeTab === 'main' ? '標準検索' : '詳細検索'}</strong>
          </span>
        </div>
      )}

      {error && (
        <div className="error-message">
          ❌ エラー: {error}
        </div>
      )}

      {activeTab === 'main' && results.length > 0 && (
        <div className="results-section">
          <h2>検索結果 ({results.length}件)</h2>
          <div className="results-grid">
            {results.map((result) => (
              <div key={result.id} className="result-card">
                <div className="result-header">
                  <h3 className="result-title">{result.title}</h3>
                  <span className="result-type">{result.file_type || 'unknown'}</span>
                </div>
                {result.description && (
                  <p className="result-description">{result.description}</p>
                )}
                <div className="result-content">
                  {formatContent(result.formatted_text)}
                </div>
                <div className="result-metadata">
                  <span className="result-id">ID: {result.id}</span>
                  <span className="result-date">
                    {new Date(result.uploaded_at).toLocaleString('ja-JP')}
                  </span>
                </div>
                {result.s3_key && (
                  <div className="result-s3">
                    S3: {result.s3_key}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'debug' && debugResults.length > 0 && (
        <div className="results-section">
          <h2>詳細検索結果 ({debugResults.length}件)</h2>
          <div className="results-grid">
            {debugResults.map((result) => (
              <div key={result.id} className="result-card debug-card">
                <div className="result-header">
                  <h3 className="result-title">{result.source.title}</h3>
                  <div className="debug-info">
                    <span className="score">関連度: {result.score.toFixed(4)}</span>
                    <span className="result-type">{result.source.file_type}</span>
                  </div>
                </div>
                <div className="result-content">
                  {formatContent(result.source.content)}
                </div>
                <div className="result-metadata">
                  <span className="result-id">ID: {result.id}</span>
                  <span className="user-id">所有者: {result.source.user_id}</span>
                  <span className="result-date">
                    {new Date(result.source.uploaded_at).toLocaleString('ja-JP')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {(results.length === 0 && debugResults.length === 0 && searchStats && !loading) && (
        <div className="no-results">
          😅 "{searchStats.query}" に関連するドキュメントが見つかりませんでした
        </div>
      )}

      <div className="test-queries">
        <h3>検索例</h3>
        <div className="query-buttons">
          <button onClick={() => setQuery('Python')} className="query-btn">Python</button>
          <button onClick={() => setQuery('AWS')} className="query-btn">AWS</button>
          <button onClick={() => setQuery('機械学習')} className="query-btn">機械学習</button>
          <button onClick={() => setQuery('Pyhton')} className="query-btn">Pyhton (スペルミス)</button>
          <button onClick={() => setQuery('存在しないキーワード')} className="query-btn">存在しないキーワード</button>
        </div>
      </div>
    </div>
  );
};

export default SearchDebug;
