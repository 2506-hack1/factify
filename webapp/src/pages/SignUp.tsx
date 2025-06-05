import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import './Auth.css';

const SignUp: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'signup' | 'confirm'>('signup');

  const { signUp, confirmSignUp } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      setError('メールアドレスとパスワードを入力してください');
      return;
    }

    if (password !== confirmPassword) {
      setError('パスワードが一致しません');
      return;
    }

    if (password.length < 8) {
      setError('パスワードは8文字以上で入力してください');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Cognitoではメールアドレスをユーザー名として使用
      await signUp(email, password);
      showToast('確認メールを送信しました。メールをご確認ください。', 'success');
      setStep('confirm');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'サインアップに失敗しました';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!confirmationCode) {
      setError('確認コードを入力してください');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await confirmSignUp(email, confirmationCode);
      navigate('/signin', { 
        state: { message: 'アカウントが確認されました。サインインしてください。' }
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'アカウント確認に失敗しました';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (step === 'confirm') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>アカウント確認</h2>
          <p>登録したメールアドレスに確認コードを送信しました。</p>
          <form onSubmit={handleConfirm} className="auth-form">
            <div className="form-group">
              <label htmlFor="confirmationCode">確認コード</label>
              <input
                type="text"
                id="confirmationCode"
                value={confirmationCode}
                onChange={(e) => setConfirmationCode(e.target.value)}
                placeholder="確認コード"
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? '確認中...' : 'アカウントを確認'}
            </button>
          </form>

          <div className="auth-links">
            <button 
              onClick={() => setStep('signup')} 
              className="link-button"
              disabled={loading}
            >
              戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>サインアップ</h2>
        <form onSubmit={handleSignUp} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="メールアドレス"
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
              placeholder="パスワード（8文字以上）"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">パスワード確認</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="パスワードを再入力"
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'サインアップ中...' : 'サインアップ'}
          </button>
        </form>

        <div className="auth-links">
          <p>
            すでにアカウントをお持ちの方は{' '}
            <Link to="/signin">こちらからサインイン</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
