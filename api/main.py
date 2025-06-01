from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import re
import boto3
import os
import uuid
from datetime import datetime
import io

app = FastAPI()

# AWSリソース設定
REGION_NAME = "ap-northeast-1"
DYNAMODB_TABLE_NAME = "factify-dynamodb-table"
S3_BUCKET_NAME = "factify-s3-bucket"

# AWS クライアント初期化
s3_client = boto3.client('s3', region_name=REGION_NAME)
dynamodb_client = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)

# テキストの正規化を行う
def clean_text(raw_text: str) -> str:
    # 全角スペースやタブを半角スペースに変換
    text = raw_text.replace("\u3000", " ").replace("\t", " ")
    # 改行もスペースに置換
    text = text.replace("\r", " ").replace("\n", " ")
    # 複数スペースを1つにする
    text = re.sub(r" +", " ", text)
    return text.strip()

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
    テキストファイルをアップロードしてS3に保存し、メタデータをDynamoDBに格納します
    """
    try:
        # ファイルの内容を読み込む
        file_content = await file.read()
        
        # ファイルタイプの確認（今回はテキストファイルのみ受け付ける）
        if not file.content_type.startswith('text/'):
            raise HTTPException(status_code=400, detail="テキストファイルのみアップロード可能です")
        
        # ファイル名と拡張子を取得
        file_name = file.filename
        file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')
        
        # UUIDを生成してS3のキーとして使用
        file_id = str(uuid.uuid4())
        s3_key = f"texts/{file_id}.{file_extension}"
        
        # S3にファイルをアップロード
        s3_client.upload_fileobj(
            io.BytesIO(file_content),
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        # 現在のタイムスタンプをISO 8601形式で取得
        uploaded_at = datetime.utcnow().isoformat()
        
        # DynamoDBにメタデータを保存
        item = {
            "id": file_id,
            "s3_key": s3_key,
            "file_name": file_name,
            "file_type": file_extension,
            "uploaded_at": uploaded_at,
            "title": title,
            "description": description or ""
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