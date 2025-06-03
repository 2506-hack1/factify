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
