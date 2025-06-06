"""
データモデル定義
DynamoDBのドキュメント構造とAPIレスポンス用のモデル
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Document(BaseModel):
    """
    DynamoDBに保存されるドキュメントを表現するモデル
    """
    id: str
    s3_key: str
    file_name: str
    file_type: str
    formatted_text: str
    uploaded_at: str
    title: str
    description: str
    extracted_metadata: Dict[str, Any]


class SearchRequest(BaseModel):
    """
    検索リクエスト用モデル
    """
    query: str
    language: Optional[str] = "en"
    max_results: Optional[int] = 5
    user_only: Optional[bool] = False  # ユーザー固有のファイルのみを検索するかどうか


class SearchResponse(BaseModel):
    """
    検索レスポンス用モデル
    """
    success: bool
    query: str
    total_results: int
    results: List[Document]


class UploadResponse(BaseModel):
    """
    ファイルアップロードレスポンス用モデル
    """
    success: bool
    file_id: str
    message: str
    metadata: Document


class AccessLog(BaseModel):
    """
    アクセス履歴記録用モデル
    """
    transaction_id: str
    accessed_document_id: str
    accessing_user_id: str
    document_owner_id: str
    timestamp: str
    search_query: str
    search_rank: int
    access_type: str  # "search_result", "view", "download"


class IncentiveSummary(BaseModel):
    """
    インセンティブ集計用モデル
    """
    owner_user_id: str
    period: str  # YYYY-MM形式
    total_access_count: int
    unique_users_count: int
    total_incentive_points: int
    document_access_details: Dict[str, Any]


class IncentiveRequest(BaseModel):
    """
    インセンティブ取得リクエスト用モデル
    """
    user_id: Optional[str] = None
    period: Optional[str] = None  # YYYY-MM形式
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class IncentiveResponse(BaseModel):
    """
    インセンティブレスポンス用モデル
    """
    success: bool
    user_id: str
    period: str
    summary: IncentiveSummary
    detailed_logs: List[AccessLog]
