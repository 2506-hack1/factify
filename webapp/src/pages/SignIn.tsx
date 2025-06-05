import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import './Auth.css';

const SignIn: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signIn } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  // リダイレクト先を取得（デフォルトは/upload）
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/upload';
  const successMessage = (location.state as { message?: string })?.message;

  // ページロード時に成功メッセージがあれば表示
  useEffect(() => {
    if (successMessage) {
      showToast(successMessage, 'success');
    }
  }, [successMessage, showToast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('ユーザー名とパスワードを入力してください');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await signIn(username, password);
      showToast('ログインが成功しました', 'success');
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'サインインに失敗しました';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>サインイン</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">ユーザー名 / メールアドレス</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="ユーザー名またはメールアドレス"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="パスワード"
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'サインイン中...' : 'サインイン'}
          </button>
        </form>

        <div className="auth-links">
          <p>
            アカウントをお持ちでない方は{' '}
            <Link to="/signup">こちらからサインアップ</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
