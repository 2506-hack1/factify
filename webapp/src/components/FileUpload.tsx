import React, { useState, useRef, type ChangeEvent, type DragEvent } from 'react';
import { uploadService, type UploadResponse } from '../services/uploadService';
import { useToast } from '../hooks/useToast';
import './FileUpload.css';

interface FileUploadProps {
  onUploadSuccess?: (response: UploadResponse) => void;
  onUploadError?: (error: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { addToast } = useToast();

  const handleFileSelect = (file: File) => {
    if (!uploadService.isSupportedFileType(file)) {
      const errorMsg = 'サポートされていないファイル形式です。テキスト、HTML、PDF、Word文書のみ対応しています。';
      addToast(errorMsg, 'error');
      onUploadError?.(errorMsg);
      return;
    }

    if (!uploadService.isValidFileSize(file)) {
      const errorMsg = 'ファイルサイズが10MBを超えています。';
      addToast(errorMsg, 'error');
      onUploadError?.(errorMsg);
      return;
    }

    setSelectedFile(file);
    // ファイル名からタイトルを自動生成（拡張子を除去）
    const fileName = file.name.replace(/\.[^/.]+$/, '');
    setTitle(fileName);
  };

  const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !title.trim()) {
      addToast('ファイルとタイトルを入力してください。', 'error');
      return;
    }

    setIsUploading(true);
    try {
      const response = await uploadService.uploadFile(
        selectedFile,
        title.trim(),
        description.trim() || undefined
      );

      addToast('ファイルのアップロードが完了しました！', 'success');
      onUploadSuccess?.(response);
      
      // フォームをリセット
      setSelectedFile(null);
      setTitle('');
      setDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'アップロード中にエラーが発生しました。';
      addToast(errorMsg, 'error');
      onUploadError?.(errorMsg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setTitle('');
    setDescription('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="file-upload">
      <div className="upload-section">
        <h3>ファイルアップロード</h3>
        
        {/* ドラッグ&ドロップエリア */}
        <div
          className={`upload-dropzone ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.html,.pdf,.docx"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />
          
          {selectedFile ? (
            <div className="selected-file">
              <div className="file-icon">📄</div>
              <div className="file-info">
                <div className="file-name">{selectedFile.name}</div>
                <div className="file-details">
                  {uploadService.getFileTypeDisplayName(selectedFile.type)} • {formatFileSize(selectedFile.size)}
                </div>
              </div>
              <button
                type="button"
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveFile();
                }}
              >
                ✕
              </button>
            </div>
          ) : (
            <div className="upload-prompt">
              <div className="upload-icon">📁</div>
              <div className="upload-text">
                <div>ファイルをドラッグ&ドロップ</div>
                <div>または<span className="click-text">クリックして選択</span></div>
              </div>
              <div className="supported-formats">
                対応形式: テキスト、HTML、PDF、Word文書（最大10MB）
              </div>
            </div>
          )}
        </div>

        {/* フォーム */}
        {selectedFile && (
          <div className="upload-form">
            <div className="form-group">
              <label htmlFor="title">タイトル *</label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="ファイルのタイトルを入力してください"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">説明（オプション）</label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="ファイルの説明や内容について（任意）"
                rows={3}
              />
            </div>

            <div className="upload-actions">
              <button
                type="button"
                className="upload-btn"
                onClick={handleUpload}
                disabled={isUploading || !title.trim()}
              >
                {isUploading ? (
                  <>
                    <span className="loading-spinner">⏳</span>
                    アップロード中...
                  </>
                ) : (
                  '📤 アップロード'
                )}
              </button>
              
              <button
                type="button"
                className="cancel-btn"
                onClick={handleRemoveFile}
                disabled={isUploading}
              >
                キャンセル
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
