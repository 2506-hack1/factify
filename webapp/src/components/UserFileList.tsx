import React, { useState, useEffect } from 'react';
import { uploadService, type UserFile } from '../services/uploadService';
import { useToast } from '../hooks/useToast';
import './UserFileList.css';

interface UserFileListProps {
  refreshTrigger?: number;
  onFileDeleted?: () => void;
}

export const UserFileList: React.FC<UserFileListProps> = ({
  refreshTrigger,
  onFileDeleted
}) => {
  const [files, setFiles] = useState<UserFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const { addToast } = useToast();

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await uploadService.getUserFiles();
      setFiles(response.files);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'ファイル一覧の取得に失敗しました。';
      addToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [refreshTrigger]);

  const handleDelete = async (fileId: string, fileName: string) => {
    if (!confirm(`「${fileName}」を削除してもよろしいですか？この操作は取り消せません。`)) {
      return;
    }

    try {
      setDeleting(fileId);
      await uploadService.deleteFile(fileId);
      addToast('ファイルが削除されました。', 'success');
      
      // ファイル一覧から削除
      setFiles(files.filter(file => file.id !== fileId));
      onFileDeleted?.();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'ファイルの削除に失敗しました。';
      addToast(errorMsg, 'error');
    } finally {
      setDeleting(null);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileTypeIcon = (fileType: string): string => {
    switch (fileType) {
      case 'text/plain':
        return '📝';
      case 'text/html':
        return '🌐';
      case 'application/pdf':
        return '📄';
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return '📘';
      default:
        return '📄';
    }
  };

  const getFileTypeDisplayName = (fileType: string): string => {
    switch (fileType) {
      case 'text/plain':
        return 'テキスト';
      case 'text/html':
        return 'HTML';
      case 'application/pdf':
        return 'PDF';
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'Word';
      default:
        return 'その他';
    }
  };

  if (loading) {
    return (
      <div className="user-file-list">
        <div className="loading-state">
          <div className="loading-spinner">⏳</div>
          <div>ファイル一覧を読み込み中...</div>
        </div>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="user-file-list">
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <div className="empty-text">
            <h3>アップロードされたファイルがありません</h3>
            <p>最初のファイルをアップロードしてみましょう。</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-file-list">
      <div className="file-list-header">
        <h3>アップロード済みファイル ({files.length}件)</h3>
        <button
          className="refresh-btn"
          onClick={loadFiles}
          disabled={loading}
        >
          🔄 更新
        </button>
      </div>

      <div className="file-grid">
        {files.map((file) => (
          <div key={file.id} className="file-card">
            <div className="file-card-header">
              <div className="file-icon">
                {getFileTypeIcon(file.file_type)}
              </div>
              <div className="file-type-badge">
                {getFileTypeDisplayName(file.file_type)}
              </div>
              <button
                className="delete-btn"
                onClick={() => handleDelete(file.id, file.file_name)}
                disabled={deleting === file.id}
                title="ファイルを削除"
              >
                {deleting === file.id ? '⏳' : '🗑️'}
              </button>
            </div>

            <div className="file-card-body">
              <h4 className="file-title">{file.title}</h4>
              <div className="file-name">{file.file_name}</div>
              {file.description && (
                <div className="file-description">{file.description}</div>
              )}
            </div>

            <div className="file-card-footer">
              <div className="upload-date">
                {formatDate(file.uploaded_at)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
