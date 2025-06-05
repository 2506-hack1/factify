import { api } from './apiClient';

export interface UploadResponse {
  success: boolean;
  file_id: string;
  message: string;
  metadata: any;
}

export interface UserFile {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  uploaded_at: string;
  description: string;
  s3_key: string;
}

export interface UserFilesResponse {
  success: boolean;
  user_id: string;
  total_files: number;
  files: UserFile[];
}

export interface UserStatsResponse {
  success: boolean;
  user_id: string;
  username: string;
  email: string;
  statistics: {
    total_files: number;
    file_types: Record<string, number>;
    total_text_length: number;
    average_text_length: number;
  };
}

export class UploadService {
  /**
   * ファイルをアップロードする
   */
  async uploadFile(file: File, title: string, description?: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) {
      formData.append('description', description);
    }

    return api.post<UploadResponse>('/upload/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * ユーザーのファイル一覧を取得する
   */
  async getUserFiles(): Promise<UserFilesResponse> {
    return api.get<UserFilesResponse>('/files/user');
  }

  /**
   * ユーザーの統計情報を取得する
   */
  async getUserStats(): Promise<UserStatsResponse> {
    return api.get<UserStatsResponse>('/files/user/stats');
  }

  /**
   * ユーザーのファイルを削除する
   */
  async deleteFile(fileId: string): Promise<{ success: boolean; message: string }> {
    return api.delete(`/files/user/${fileId}`);
  }

  /**
   * サポートされているファイルタイプをチェックする
   */
  isSupportedFileType(file: File): boolean {
    const supportedTypes = [
      'text/plain',
      'text/html',
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    return supportedTypes.includes(file.type);
  }

  /**
   * ファイルサイズをチェックする（10MB制限）
   */
  isValidFileSize(file: File, maxSizeInMB: number = 10): boolean {
    const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
    return file.size <= maxSizeInBytes;
  }

  /**
   * ファイルの拡張子を取得する
   */
  getFileExtension(fileName: string): string {
    return fileName.split('.').pop()?.toLowerCase() || '';
  }

  /**
   * ファイルタイプの表示名を取得する
   */
  getFileTypeDisplayName(mimeType: string): string {
    const typeMap: Record<string, string> = {
      'text/plain': 'テキストファイル',
      'text/html': 'HTMLファイル',
      'application/pdf': 'PDFファイル',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word文書'
    };
    return typeMap[mimeType] || 'その他';
  }
}

export const uploadService = new UploadService();
