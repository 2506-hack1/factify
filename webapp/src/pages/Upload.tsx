import React from 'react';
import { useAuth } from '../hooks/useAuth';
import './Upload.css';

function Upload() {
  const { user } = useAuth();

  return (
    <div className="upload-container">
      <h1 className="upload-title">ファイルアップロード</h1>
      <div className="welcome-message">
        <p>ようこそ、<strong>{user?.username || user?.email}</strong>さん！</p>
        <p>認証されたユーザーのみがこのページにアクセスできます。</p>
      </div>
      
      <div className="upload-area">
        <h2>ファイルアップロード機能</h2>
        <p>この機能は今後実装予定です。</p>
        <p>PDFや画像ファイルをアップロードして、ファクトチェックを行います。</p>
      </div>
    </div>
  );
}

export default Upload;
