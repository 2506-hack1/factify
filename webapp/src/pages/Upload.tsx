import React from 'react';
import { useAuth } from '../hooks/useAuth';

function Upload() {
  const { user } = useAuth();

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>ファイルアップロード</h1>
      <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#f0f9ff', borderRadius: '8px' }}>
        <p>ようこそ、<strong>{user?.username || user?.email}</strong>さん！</p>
        <p>認証されたユーザーのみがこのページにアクセスできます。</p>
      </div>
      
      <div style={{ padding: '2rem', border: '2px dashed #e5e7eb', borderRadius: '8px', textAlign: 'center' }}>
        <h2>ファイルアップロード機能</h2>
        <p>この機能は今後実装予定です。</p>
        <p>PDFや画像ファイルをアップロードして、ファクトチェックを行います。</p>
      </div>
    </div>
  );
}

export default Upload;
