from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, List, Tuple
import re
import boto3
import os
import uuid
from datetime import datetime
import io
import fitz  # PyMuPDF
from docx import Document
from bs4 import BeautifulSoup

from config import (
    REGION_NAME, 
    DYNAMODB_TABLE_NAME, 
    S3_BUCKET_NAME,
    SUPPORTED_FILE_TYPES
)
from text_processors import clean_text, format_for_ai
from file_extractors import extract_content_by_type

app = FastAPI()

# AWS クライアント初期化
s3_client = boto3.client('s3', region_name=REGION_NAME)
dynamodb_client = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)

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
        original_file_name = file.filename
        file_name_parts = os.path.splitext(original_file_name)
        file_name = file_name_parts[0]  # 拡張子なしのファイル名
        file_extension = file_name_parts[1].lower().lstrip('.')  # 拡張子（ピリオドなし）
        
        # ファイルの内容からテキストとメタデータを抽出
        extracted_text, file_metadata = extract_content_by_type(file_content, file.content_type)
        
        # ファイルタイプに応じてタイトルを生成
        auto_title = title
        if title == "" or title is None:
            if file.content_type == 'text/plain':
                # プレーンテキストファイルの場合、最初の20文字をタイトルとして使用
                auto_title = extracted_text[:20] + ("..." if len(extracted_text) > 20 else "")
            elif file.content_type == 'text/html':
                # HTMLファイルの場合、メタデータからタイトルを抽出
                if 'html_title' in file_metadata:
                    auto_title = file_metadata['html_title']
                else:
                    # HTMLにタイトルがない場合は最初の20文字を使用
                    auto_title = extracted_text[:20] + ("..." if len(extracted_text) > 20 else "") if extracted_text else file_name
            elif file.content_type == 'application/pdf':
                # PDFファイルの場合、メタデータからタイトルを抽出
                if 'pdf_title' in file_metadata:
                    auto_title = file_metadata['pdf_title']
                else:
                    # PDFにタイトルがない場合はファイル名を使用
                    auto_title = file_name
            elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                # Docxファイルの場合、メタデータからタイトルを抽出
                if 'docx_title' in file_metadata:
                    auto_title = file_metadata['docx_title']
                else:
                    # Docxにタイトルがない場合は最初の20文字を使用
                    auto_title = extracted_text[:20] + ("..." if len(extracted_text) > 20 else "") if extracted_text else file_name
        
        # UUIDを生成して使用
        file_id = str(uuid.uuid4())
        
        # 現在のタイムスタンプをISO 8601形式で取得
        uploaded_at = datetime.utcnow().isoformat()
        
        # AIモデル用にテキストデータを整形
        metadata_for_ai = {
            "title": auto_title,
            "description": description or "",
            "file_type": file_extension,
            "file_name": file_name,
            "uploaded_at": uploaded_at,
            **file_metadata
        }
        
        # AI用に整形したテキストを生成
        formatted_text = format_for_ai(extracted_text, metadata_for_ai)
        
        # S3キーを生成（拡張子をtxtに変更）
        s3_key = f"data/{file_id}.txt"
        
        # S3に整形済みテキストをアップロード
        s3_client.put_object(
            Body=formatted_text.encode('utf-8'),
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            ContentType='text/plain; charset=utf-8'
        )
        
        # DynamoDBにメタデータを保存
        item = {
            "id": file_id,
            "s3_key": s3_key,
            "file_name": file_name,
            "file_type": file_extension,
            "uploaded_at": uploaded_at,
            "title": auto_title,
            "description": description or "",
            "content_type": file.content_type,
            # 抽出したメタデータも追加
            "extracted_metadata": file_metadata
        }
        
        table.put_item(Item=item)
        
        return {
            "success": True,
            "file_id": file_id,
            "message": "ファイルがアップロードされました",
            "metadata": item
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"アップロード中にエラーが発生しました: {str(e)}")
