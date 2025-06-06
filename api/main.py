import os

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
from src.models import Document, SearchRequest, SearchResponse, UploadResponse, AccessLog, IncentiveRequest, IncentiveResponse, IncentiveSummary
from src.auth.cognito_auth import get_current_user, get_current_user_optional, require_admin
from src.services.opensearch_service import opensearch_service
from src.services.access_logger_service import access_logger_service
from src.config import S3_BUCKET_NAME
from boto3.dynamodb.conditions import Attr

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",  # 開発用
        "https://d2gf2wvyuful49.cloudfront.net"  # 本番用CloudFront
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return HTMLResponse("<h1>Hello from FastAPI on Fargate!</h1>")

@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント - ECSとALBで使用
    """
    try:
        # 基本的なヘルスチェック
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {}
        }
        
        # DynamoDBヘルスチェック
        try:
            aws_services.get_dynamodb_table().describe_table()
            health_status["services"]["dynamodb"] = "healthy"
        except Exception as e:
            health_status["services"]["dynamodb"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # OpenSearchヘルスチェック（オプション）
        try:
            if opensearch_service.health_check():
                health_status["services"]["opensearch"] = "healthy"
            else:
                health_status["services"]["opensearch"] = "unhealthy"
        except Exception as e:
            health_status["services"]["opensearch"] = f"error: {str(e)}"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/admin/opensearch/init")
async def init_opensearch(current_user: dict = Depends(require_admin)):
    """
    OpenSearchインデックス初期化（管理者専用）
    """
    try:
        # ヘルスチェック
        if not opensearch_service.health_check():
            raise HTTPException(
                status_code=503, 
                detail="OpenSearchクラスターに接続できません"
            )
        
        # インデックス作成
        result = opensearch_service.create_index()
        
        if "error" in result:
            raise HTTPException(
                status_code=500, 
                detail=f"インデックス作成に失敗しました: {result['error']}"
            )
        
        return {
            "success": True,
            "message": "OpenSearchインデックスが正常に作成されました",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OpenSearch初期化エラー: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"初期化中にエラーが発生しました: {str(e)}"
        )


@app.get("/admin/opensearch/status")
async def opensearch_status(current_user: dict = Depends(require_admin)):
    """
    OpenSearchステータス確認（管理者専用）
    """
    try:
        health_status = opensearch_service.health_check()
        
        return {
            "success": True,
            "opensearch_healthy": health_status,
            "endpoint": opensearch_service.endpoint,
            "index_name": opensearch_service.index_name
        }
        
    except Exception as e:
        print(f"OpenSearchステータス確認エラー: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"ステータス確認中にエラーが発生しました: {str(e)}"
        )


@app.post("/admin/opensearch/migrate")
async def migrate_data_to_opensearch(current_user: dict = Depends(require_admin)):
    """
    既存DynamoDBデータをOpenSearchに移行（管理者専用）
    """
    try:
        # OpenSearchヘルスチェック
        if not opensearch_service.health_check():
            raise HTTPException(
                status_code=503, 
                detail="OpenSearchクラスターに接続できません"
            )
        
        # DynamoDBから全データを取得
        response = aws_services.get_dynamodb_table().scan()
        items = response.get('Items', [])
        
        successful_migrations = 0
        failed_migrations = 0
        
        for item in items:
            try:
                # DynamoDBアイテムからOpenSearch用データを作成
                opensearch_result = opensearch_service.index_document(
                    doc_id=item["id"],
                    title=item.get("title", ""),
                    content=item.get("formatted_text", ""),
                    user_id=item.get("user_id", "anonymous"),
                    file_type=item.get("file_type", "unknown"),
                    uploaded_at=item.get("uploaded_at")
                )
                
                if "error" not in opensearch_result:
                    successful_migrations += 1
                else:
                    failed_migrations += 1
                    print(f"移行失敗: {item['id']} - {opensearch_result.get('error')}")
                    
            except Exception as migration_error:
                failed_migrations += 1
                print(f"移行エラー: {item.get('id', 'unknown')} - {migration_error}")
        
        return {
            "success": True,
            "message": "データ移行が完了しました",
            "statistics": {
                "total_items": len(items),
                "successful_migrations": successful_migrations,
                "failed_migrations": failed_migrations
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"データ移行エラー: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"データ移行中にエラーが発生しました: {str(e)}"
        )

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
        
        # OpenSearchにもドキュメントを登録（エラーが発生してもアップロード処理は継続）
        try:
            opensearch_result = opensearch_service.index_document(
                doc_id=file_id,
                title=auto_title,
                content=formatted_text,
                user_id=current_user.get("user_id", "anonymous"),
                file_type=file_extension,
                uploaded_at=uploaded_at
            )
            print(f"OpenSearch登録結果: {opensearch_result}")
        except Exception as opensearch_error:
            print(f"OpenSearch登録エラー（無視して処理継続）: {opensearch_error}")
        
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
async def search_documents(search_request: SearchRequest, current_user: dict = Depends(get_current_user_optional)):
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
            user_id = current_user.get("user_id") if current_user else None  # 認証オプションなのでcurrent_userがNoneの可能性あり
        
        # OpenSearchで検索を試行（フォールバック付き）
        search_results = []
        opensearch_success = False
        
        try:
            # OpenSearchが利用可能かチェック
            if opensearch_service.health_check():
                print("OpenSearchで検索実行中...")
                opensearch_response = opensearch_service.search(
                    query=search_request.query,
                    user_id=user_id,
                    size=search_request.max_results
                )
                
                if "error" not in opensearch_response and "hits" in opensearch_response:
                    # OpenSearchの結果をDynamoDBフォーマットに変換
                    for hit in opensearch_response["hits"]["hits"][:search_request.max_results]:
                        source = hit["_source"]
                        # OpenSearchからDynamoDBの詳細データを取得
                        try:
                            dynamodb_item = aws_services.get_dynamodb_table().get_item(
                                Key={"id": hit["_id"]}
                            ).get("Item")
                            if dynamodb_item:
                                search_results.append(dynamodb_item)
                        except Exception as db_error:
                            print(f"DynamoDB取得エラー: {db_error}")
                            continue
                    
                    opensearch_success = True
                    print(f"OpenSearch検索成功: {len(search_results)}件")
                else:
                    print(f"OpenSearch応答エラー: {opensearch_response}")
            else:
                print("OpenSearchヘルスチェック失敗")
        except Exception as opensearch_error:
            print(f"OpenSearch検索エラー: {opensearch_error}")
        
        # OpenSearchが失敗した場合はDynamoDBフォールバック
        if not opensearch_success:
            print("DynamoDBフォールバック検索実行中...")
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
        
        # 🎯 アクセス履歴記録（非同期・ノンブロッキング）
        if current_user and search_results:
            try:
                accessing_user_id = current_user.get("user_id")
                if accessing_user_id:
                    # バックグラウンドでアクセス記録（エラーが発生しても検索レスポンスには影響しない）
                    access_logger_service.log_search_access(
                        accessed_documents=search_results,
                        accessing_user_id=accessing_user_id,
                        search_query=search_request.query
                    )
            except Exception as log_error:
                print(f"アクセス記録エラー（無視して処理継続）: {log_error}")
        
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

@app.post("/debug/opensearch/search")
async def debug_opensearch_search(search_data: dict):
    """
    デバッグ用OpenSearch検索エンドポイント（認証不要）
    """
    try:
        query = search_data.get("query", "")
        user_id = search_data.get("user_id")
        size = search_data.get("size", 10)
        
        if not query:
            return {"error": "クエリが必要です"}
        
        # OpenSearchで直接検索
        if query == "*" or query == "":
            # 全ドキュメント取得用の特別なクエリ
            import requests
            from requests.auth import HTTPBasicAuth
            search_body = {
                "query": {"match_all": {}},
                "size": size
            }
            if user_id:
                search_body["query"] = {
                    "bool": {
                        "must": [{"match_all": {}}],
                        "filter": [{"term": {"user_id": user_id}}]
                    }
                }
            
            try:
                response = requests.post(
                    f"{opensearch_service.endpoint}/{opensearch_service.index_name}/_search",
                    json=search_body,
                    headers={"Content-Type": "application/json"},
                    auth=opensearch_service.auth,
                    verify=opensearch_service.verify_ssl,
                    timeout=10
                )
                result = response.json()
            except Exception as e:
                return {"error": str(e)}
        else:
            result = opensearch_service.search_documents(query, user_id=user_id, size=size)
        
        if "error" in result:
            return {"error": result["error"]}
        
        hits = result.get("hits", {}).get("hits", [])
        
        return {
            "success": True,
            "query": query,
            "user_id": user_id,
            "total_hits": result.get("hits", {}).get("total", {}).get("value", 0),
            "returned_hits": len(hits),
            "results": [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"]
                }
                for hit in hits
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}


# ==================== インセンティブ・アクセス履歴管理API ====================

@app.get("/access-logs/user", response_model=dict)
async def get_user_access_logs(current_user: dict = Depends(get_current_user)):
    """
    認証されたユーザーのアクセス履歴を取得します
    """
    try:
        user_id = current_user.get("user_id")
        
        access_logs = access_logger_service.get_user_access_logs(
            user_id=user_id,
            limit=100
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "total_logs": len(access_logs),
            "access_logs": access_logs
        }
        
    except Exception as e:
        print(f"アクセス履歴取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"アクセス履歴取得中にエラーが発生しました: {str(e)}")


@app.get("/analytics/weekly-users", response_model=dict)
async def get_weekly_user_activity(
    days: Optional[int] = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    過去N日間の日別ユニークユーザー数を取得します
    
    Parameters:
    -----------
    days : int, optional
        遡る日数（デフォルト: 7日間）
    """
    try:
        # 週間ユーザーアクティビティデータを取得
        weekly_data = access_logger_service.get_weekly_user_activity(days=days)
        
        return weekly_data
        
    except Exception as e:
        print(f"週間ユーザーアクティビティ取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"週間ユーザーアクティビティ取得中にエラーが発生しました: {str(e)}")


@app.get("/incentive/user", response_model=dict)
async def get_user_incentive_summary(
    period: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    認証されたユーザーのインセンティブ集計を取得します
    
    Parameters:
    -----------
    period : str, optional
        対象月 (YYYY-MM形式、未指定の場合は当月)
    """
    try:
        user_id = current_user.get("user_id")
        
        # 期間が未指定の場合は当月を使用
        if not period:
            from datetime import datetime
            period = datetime.now().strftime("%Y-%m")
        
        # インセンティブポイントを計算
        incentive_data = access_logger_service.calculate_incentive_points(
            owner_user_id=user_id,
            period_month=period
        )
        
        if not incentive_data:
            return {
                "success": True,
                "user_id": user_id,
                "period": period,
                "total_access_count": 0,
                "unique_users_count": 0,
                "total_incentive_points": 0,
                "document_access_details": {}
            }
        
        # 集計結果を保存
        access_logger_service.save_incentive_summary(incentive_data)
        
        return {
            "success": True,
            **incentive_data
        }
        
    except Exception as e:
        print(f"インセンティブ取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"インセンティブ取得中にエラーが発生しました: {str(e)}")


@app.get("/incentive/document/{document_id}", response_model=dict)
async def get_document_access_stats(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    指定されたドキュメントのアクセス統計を取得します
    """
    try:
        user_id = current_user.get("user_id")
        
        # ドキュメントの所有者確認
        response = aws_services.get_dynamodb_table().get_item(
            Key={'id': document_id}
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")
        
        document_item = response['Item']
        document_owner_id = document_item.get('user_id')
        
        # 所有者チェック
        if document_owner_id != user_id:
            raise HTTPException(status_code=403, detail="このドキュメントの統計を確認する権限がありません")
        
        # アクセス統計を取得
        access_stats = access_logger_service.get_document_access_stats(
            document_id=document_id,
            period_days=30
        )
        
        return {
            "success": True,
            "document_info": {
                "id": document_id,
                "title": document_item.get('title', ''),
                "file_name": document_item.get('file_name', ''),
                "uploaded_at": document_item.get('uploaded_at', '')
            },
            **access_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ドキュメント統計取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"統計取得中にエラーが発生しました: {str(e)}")


@app.post("/admin/incentive/batch-calculate")
async def batch_calculate_incentives(current_user: dict = Depends(require_admin)):
    """
    全ユーザーのインセンティブを一括計算します（管理者専用）
    """
    try:
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        
        # 全ユーザーを取得
        response = aws_services.get_dynamodb_table().scan()
        items = response.get('Items', [])
        
        # ユニークなユーザーIDを抽出
        user_ids = set()
        for item in items:
            user_id = item.get('user_id')
            if user_id and user_id != 'anonymous':
                user_ids.add(user_id)
        
        processed_users = 0
        failed_users = 0
        
        for user_id in user_ids:
            try:
                # インセンティブ計算
                incentive_data = access_logger_service.calculate_incentive_points(
                    owner_user_id=user_id,
                    period_month=current_month
                )
                
                if incentive_data:
                    # 集計結果を保存
                    access_logger_service.save_incentive_summary(incentive_data)
                    processed_users += 1
                
            except Exception as user_error:
                print(f"ユーザー {user_id} のインセンティブ計算エラー: {user_error}")
                failed_users += 1
        
        return {
            "success": True,
            "message": "インセンティブ一括計算が完了しました",
            "statistics": {
                "total_users": len(user_ids),
                "processed_users": processed_users,
                "failed_users": failed_users,
                "period": current_month
            }
        }
        
    except Exception as e:
        print(f"インセンティブ一括計算エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"一括計算中にエラーが発生しました: {str(e)}")
