import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Navigation.css';

const Navigation: React.FC = () => {
  const { user, isAuthenticated, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          Factify
        </Link>

        <div className="nav-links">
          <Link to="/" className="nav-link">ホーム</Link>
          <Link to="/about" className="nav-link">About</Link>
          
          {isAuthenticated ? (
            <>
              <Link to="/upload" className="nav-link">アップロード</Link>
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
              <Link to="/signin" className="nav-button signin">
                サインイン
              </Link>
              <Link to="/signup" className="nav-button signup">
                サインアップ
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
