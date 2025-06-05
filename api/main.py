import os
from dotenv import load_dotenv

# 開発環境で.envファイルを読み込み
if os.path.exists('.env'):
    load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
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
from src.models import Document, SearchRequest, SearchResponse, UploadResponse
from src.auth.cognito_auth import get_current_user, get_current_user_mock, get_current_user_optional, require_admin
from src.config import S3_BUCKET_NAME
from boto3.dynamodb.conditions import Attr

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発用
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return HTMLResponse("<h1>Hello from FastAPI on Fargate!</h1>")

@app.get("/debug/config")
async def debug_config():
    """デバッグ用：設定確認エンドポイント"""
    return {
        "debug_mode": os.getenv("AUTH_DEBUG_MODE"),
        "cognito_region": os.getenv("COGNITO_REGION"),
        "user_pool_id_set": bool(os.getenv("COGNITO_USER_POOL_ID")),
        "client_id_set": bool(os.getenv("COGNITO_CLIENT_ID"))
    }

# 認証テスト用エンドポイント
@app.get("/auth/test")
async def test_auth(current_user: dict = Depends(get_current_user_mock)):
    """認証テスト用エンドポイント（認証必須）"""
    return {
        "message": "Authentication successful",
        "user": current_user,
        "endpoint": "test_auth"
    }

@app.get("/auth/test-optional")
async def test_auth_optional(current_user: Optional[dict] = Depends(get_current_user_optional)):
    """認証オプショナルテスト用エンドポイント"""
    if current_user:
        return {
            "message": "Authenticated user",
            "user": current_user,
            "endpoint": "test_auth_optional"
        }
    else:
        return {
            "message": "Anonymous user",
            "user": None,
            "endpoint": "test_auth_optional"
        }

@app.get("/auth/admin-test")
async def test_admin(admin_user: dict = Depends(require_admin)):
    """管理者権限テスト用エンドポイント"""
    return {
        "message": "Admin access successful",
        "user": admin_user,
        "endpoint": "test_admin"
    }

@app.post("/upload/file", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    ファイルをアップロードしてS3に保存し、メタデータをDynamoDBに格納します
    対応ファイル形式：テキスト、HTML、PDF、Docx
    **認証必須**
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
            formatted_text=formatted_text,
            user_info=current_user  # 認証必須なので常にユーザー情報あり
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
async def search_documents(search_request: SearchRequest, current_user: dict = Depends(get_current_user)):
    """
    保存されたドキュメントを検索します（認証ユーザーのみ）
    
    Parameters:
    -----------
    search_request : SearchRequest
        検索リクエスト（query: 検索語句, language: 言語コード, max_results: 最大結果数, user_only: ユーザー固有検索）
    
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
        
        # ユーザー固有の検索かどうかを判定
        user_id = None
        if search_request.user_only:
            user_id = current_user.get("user_id")  # 認証必須なので常にcurrent_userあり
        
        # DynamoDBから検索
        search_results = aws_services.search_documents(
            query=search_request.query,
            max_results=search_request.max_results,
            user_id=user_id
        )
        
        # 言語フィルタリング（指定されている場合）
        if search_request.language and search_request.language != "en":
            filtered_results = [
                result for result in search_results 
                if result.get('language', 'en') == search_request.language
            ]
            search_results = filtered_results
        
        # Documentモデルに変換
        results = []
        for result in search_results:
            document = Document(
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
            results.append(document)
        
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

@app.get("/files/user", response_model=dict)
async def get_user_files(current_user: dict = Depends(get_current_user)):
    """
    認証されたユーザーのファイル一覧を取得します
    """
    try:
        user_id = current_user.get("user_id")
        
        # ユーザーのファイルを検索
        response = aws_services.get_dynamodb_table().scan(
            FilterExpression=Attr('user_id').eq(user_id)
        )
        
        files = response.get('Items', [])
        
        # ファイル情報を整形
        file_list = []
        for file_item in files:
            file_info = {
                "id": file_item["id"],
                "title": file_item["title"],
                "file_name": file_item["file_name"],
                "file_type": file_item["file_type"],
                "uploaded_at": file_item["uploaded_at"],
                "description": file_item.get("description", ""),
                "s3_key": file_item["s3_key"]
            }
            file_list.append(file_info)
        
        # アップロード日時で降順ソート
        file_list.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return {
            "success": True,
            "user_id": user_id,
            "total_files": len(file_list),
            "files": file_list
        }
        
    except Exception as e:
        print(f"Error getting user files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ファイル取得中にエラーが発生しました: {str(e)}")

@app.get("/files/user/stats", response_model=dict)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """
    認証されたユーザーのファイル統計を取得します
    """
    try:
        user_id = current_user.get("user_id")
        
        # ユーザーのファイルを検索
        response = aws_services.get_dynamodb_table().scan(
            FilterExpression=Attr('user_id').eq(user_id)
        )
        
        files = response.get('Items', [])
        
        # 統計を計算
        total_files = len(files)
        file_types = {}
        total_text_length = 0
        
        for file_item in files:
            # ファイルタイプの統計
            file_type = file_item.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # テキスト長の統計
            formatted_text = file_item.get("formatted_text", "")
            total_text_length += len(formatted_text)
        
        return {
            "success": True,
            "user_id": user_id,
            "username": current_user.get("username"),
            "email": current_user.get("email"),
            "statistics": {
                "total_files": total_files,
                "file_types": file_types,
                "total_text_length": total_text_length,
                "average_text_length": total_text_length // total_files if total_files > 0 else 0
            }
        }
        
    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"統計取得中にエラーが発生しました: {str(e)}")

@app.delete("/files/user/{file_id}", response_model=dict)
async def delete_user_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """
    認証されたユーザーの特定ファイルを削除します
    """
    try:
        user_id = current_user.get("user_id")
        
        # ファイルの所有者確認
        response = aws_services.get_dynamodb_table().get_item(
            Key={'id': file_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="ファイルが見つかりません")
        
        file_item = response['Item']
        file_user_id = file_item.get('user_id')
        
        # 所有者チェック
        if file_user_id != user_id:
            raise HTTPException(status_code=403, detail="このファイルを削除する権限がありません")
        
        # S3からファイルを削除
        s3_key = file_item.get('s3_key')
        if s3_key:
            try:
                aws_services.get_s3_client().delete_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key
                )
            except Exception as s3_error:
                print(f"S3削除エラー (継続): {s3_error}")
        
        # DynamoDBからレコードを削除
        aws_services.get_dynamodb_table().delete_item(
            Key={'id': file_id}
        )
        
        return {
            "success": True,
            "message": "ファイルが削除されました",
            "file_id": file_id,
            "file_name": file_item.get('file_name', 'unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting user file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ファイル削除中にエラーが発生しました: {str(e)}")
