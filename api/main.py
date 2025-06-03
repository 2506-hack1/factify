from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

from src.config import SUPPORTED_FILE_TYPES
from src.text_processors import format_for_ai
from src.file_extractors import extract_content_by_type
from src.metadata_handlers import (
    generate_auto_title,
    parse_filename,
    create_metadata_for_ai,
    create_dynamodb_item
)
from src.aws_services import aws_services

# Pydanticモデル
class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    max_results: Optional[int] = 5

class SearchResult(BaseModel):
    id: str
    s3_key: str
    file_name: str
    file_type: str
    formatted_text: str
    uploaded_at: str
    title: str
    description: str
    extracted_metadata: dict

class SearchResponse(BaseModel):
    success: bool
    query: str
    total_results: int
    results: List[SearchResult]

app = FastAPI()

@app.get("/")
async def read_root():
  return HTMLResponse("<h1>Hello from FastAPI on Fargate!</h1>")

@app.post("/upload/file", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None)
):
    """
    ファイルをアップロードしてS3に保存し、メタデータをDynamoDBに格納します
    対応ファイル形式：テキスト、HTML、PDF、Docx
    """
    try:
        # ファイルの内容を読み込む
        file_content = await file.read()
        
        # ファイルタイプの確認
        if file.content_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"サポートされていないファイルタイプです。対応形式: {', '.join(SUPPORTED_FILE_TYPES)}"
            )
        
        # ファイル名と拡張子を取得
        file_name, file_extension = parse_filename(file.filename)
        
        # ファイルの内容からテキストとメタデータを抽出
        extracted_text, file_metadata = extract_content_by_type(file_content, file.content_type)
        
        # ファイルタイプに応じてタイトルを生成
        auto_title = generate_auto_title(title, file.content_type, extracted_text, file_metadata, file_name)
        
        # UUIDを生成して使用
        file_id = str(uuid.uuid4())
        
        # 現在のタイムスタンプをISO 8601形式で取得
        uploaded_at = datetime.utcnow().isoformat()
        
        # AIモデル用にテキストデータを整形
        metadata_for_ai = create_metadata_for_ai(
            auto_title, description, file_extension, file_name, uploaded_at, file_metadata
        )
        
        # AI用に整形したテキストを生成
        formatted_text = format_for_ai(extracted_text, metadata_for_ai)
        
        # 拡張子に応じたS3フォルダを決定
        folder_name = file_extension.lower()
        
        # S3キーを生成（拡張子ごとのフォルダに保存）
        s3_key = f"{folder_name}/{file_id}.{file_extension}"
        
        # S3に元のファイルをアップロード
        aws_services.upload_file_to_s3(file_content, s3_key, file.content_type)
        
        # DynamoDBにメタデータと整形済みテキストを保存
        item = create_dynamodb_item(
            file_id=file_id, 
            s3_key=s3_key, 
            file_name=file_name, 
            file_extension=file_extension, 
            uploaded_at=uploaded_at, 
            auto_title=auto_title, 
            description=description, 
            content_type=file.content_type, 
            file_metadata=file_metadata, 
            formatted_text=formatted_text
        )
        
        aws_services.save_to_dynamodb(item)
        
        return {
            "success": True,
            "file_id": file_id,
            "message": "ファイルがアップロードされました",
            "metadata": item
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"アップロード中にエラーが発生しました: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search_documents(search_request: SearchRequest):
    """
    保存されたドキュメントを検索します
    
    Parameters:
    -----------
    search_request : SearchRequest
        検索リクエスト（query: 検索語句, language: 言語コード, max_results: 最大結果数）
    
    Returns:
    --------
    SearchResponse
        検索結果
    """
    try:
        # バリデーション
        if not search_request.query.strip():
            raise HTTPException(status_code=400, detail="検索クエリが空です")
        
        if search_request.max_results < 1 or search_request.max_results > 50:
            raise HTTPException(status_code=400, detail="max_resultsは1〜50の範囲で指定してください")
        
        # DynamoDBから検索
        search_results = aws_services.search_documents(
            query=search_request.query,
            max_results=search_request.max_results
        )
        
        # 言語フィルタリング（指定されている場合）
        if search_request.language and search_request.language != "en":
            filtered_results = [
                result for result in search_results 
                if result.get('language', 'en') == search_request.language
            ]
            search_results = filtered_results
        
        # SearchResultモデルに変換
        results = []
        for result in search_results:
            search_result = SearchResult(
                id=result['id'],  # 正確なフィールド名
                s3_key=result['s3_key'],
                file_name=result['file_name'],
                file_type=result['file_type'],
                formatted_text=result['formatted_text'],
                uploaded_at=result['uploaded_at'],
                title=result['title'],
                description=result['description'],
                extracted_metadata=result['extracted_metadata']
            )
            results.append(search_result)
        
        return SearchResponse(
            success=True,
            query=search_request.query,
            total_results=len(results),
            results=results
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        print(f"Search Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"検索中にエラーが発生しました: {str(e)}")

@app.get("/debug/scan-all")
async def debug_scan_all():
    """
    デバッグ用：DynamoDBの全データをスキャンして構造を確認
    """
    try:
        response = aws_services.get_dynamodb_table().scan()
        items = response.get('Items', [])
        
        return {
            "total_items": len(items),
            "items": items[:3] if items else [],  # 最初の3件のみ返す
            "sample_keys": list(items[0].keys()) if items else []
        }
    except Exception as e:
        return {"error": str(e)}
