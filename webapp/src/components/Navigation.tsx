import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Navigation.css';

const Navigation: React.FC = () => {
  const { user, isAuthenticated, signOut } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/');
      setIsMenuOpen(false); // メニューを閉じる
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLinkClick = () => {
    setIsMenuOpen(false); // リンククリック時にメニューを閉じる
  };

  return (
    <>
      {/* オーバーレイ */}
      <div 
        className={`nav-overlay ${isMenuOpen ? 'open' : ''}`}
        onClick={handleMenuToggle}
      />
      
      <nav className="navigation">
        <div className="nav-container">
          <Link to="/" className="nav-logo" onClick={handleLinkClick}>
            Factify
          </Link>

          {/* ハンバーガーメニューボタン */}
          <button 
            className={`hamburger-menu ${isMenuOpen ? 'open' : ''}`}
            onClick={handleMenuToggle}
            aria-label={isMenuOpen ? 'メニューを閉じる' : 'メニューを開く'}
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <div className={`nav-links ${isMenuOpen ? 'open' : ''}`}>
            <Link to="/" className="nav-link" onClick={handleLinkClick}>ホーム</Link>
            <Link to="/about" className="nav-link" onClick={handleLinkClick}>About</Link>
            <Link to="/debug/search" className="nav-link debug-link" onClick={handleLinkClick}>🔍 高度な検索</Link>
            
            {isAuthenticated ? (
              <>
                <Link to="/upload" className="nav-link" onClick={handleLinkClick}>アップロード</Link>
                <Link to="/analytics" className="nav-link" onClick={handleLinkClick}>📊 分析</Link>
                <div className="user-menu">
                  <span className="user-name">
                    {user?.username || user?.email}
                  </span>
                  <button onClick={handleSignOut} className="sign-out-button">
                    サインアウト
                  </button>
                </div>
              </>
            ) : (
              <div className="auth-buttons">
                <Link to="/signin" className="nav-button signin" onClick={handleLinkClick}>
                  サインイン
                </Link>
                <Link to="/signup" className="nav-button signup" onClick={handleLinkClick}>
                  サインアップ
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navigation;
