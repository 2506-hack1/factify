import React, { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { UserFileList } from '../components/UserFileList';
import './Upload.css';

function Upload() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    // ファイル一覧を更新
    setRefreshTrigger(prev => prev + 1);
  };

  const handleFileDeleted = () => {
    // ファイル削除時の処理（必要に応じて）
  };

  return (
    <div className="upload-container">
      <h1 className="upload-title">ファイルアップロード</h1>
      
      <div className="upload-content">
        {/* ファイルアップロードセクション */}
        <div className="upload-section">
          <FileUpload 
            onUploadSuccess={handleUploadSuccess}
          />
        </div>

        {/* ファイル一覧セクション */}
        <div className="file-list-section">
          <UserFileList 
            refreshTrigger={refreshTrigger}
            onFileDeleted={handleFileDeleted}
          />
        </div>
      </div>
    </div>
  );
}

export default Upload;
