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

def format(content: str, metadata: Dict[str, Any]) -> str:
    """
    AIモデル用にテキストを構造化して整形する
    
    Parameters:
    -----------
    content : str
        抽出されたテキスト内容
    metadata : Dict[str, Any]
        メタデータ辞書
    
    Returns:
    --------
    str
        AI用に整形されたテキスト
    """
    # テキストを正規化
    cleaned_content = clean_text(content)
    
    # 構造化されたフォーマットを作成
    formatted_text = f"TITLE: {metadata.get('title', '無題')}\n\n"
    
    if 'description' in metadata and metadata['description']:
        formatted_text += f"DESCRIPTION: {metadata['description']}\n\n"
        
    formatted_text += f"CONTENT:\n{cleaned_content}\n\n"
    
    # 重要なメタデータを追加
    formatted_text += "METADATA:\n"
    
    # ファイルタイプに応じたメタデータを追加
    if metadata.get('file_type') == 'pdf':
        if 'page_count' in metadata:
            formatted_text += f"- ページ数: {metadata['page_count']}\n"
        # PDF特有のメタデータを追加
        for key, value in metadata.items():
            if key.startswith('pdf_') and key != 'pdf_title' and value:
                formatted_text += f"- {key[4:].capitalize()}: {value}\n"
    
    # 文字数
    if 'character_count' in metadata:
        formatted_text += f"- 文字数: {metadata['character_count']}\n"
        
    # 作成日時
    if 'uploaded_at' in metadata:
        formatted_text += f"- アップロード日時: {metadata['uploaded_at']}\n"
    
    return formatted_text

# ファイルの種類に応じたコンテンツ抽出関数
def extract_content_by_type(file_content: bytes, content_type: str) -> Tuple[str, Dict[str, Any]]:
    """
    ファイルの種類に応じてコンテンツを抽出し、テキストとメタデータを返す
    
    Parameters:
    -----------
    file_content : bytes
        ファイルの内容
    content_type : str
        ファイルのMIMEタイプ
        
    Returns:
    --------
    Tuple[str, Dict[str, Any]]
        (抽出されたテキスト, メタデータ辞書)
    """
    metadata = {}
    
    if content_type.startswith('text/'):
        # テキストファイルの場合
        text = file_content.decode('utf-8')
        metadata['page_count'] = 1
        metadata['character_count'] = len(text)
        return text, metadata
        
    elif content_type == 'application/pdf':
        # PDFファイルの場合
        try:
            # PyMuPDFを使用してPDFを開く
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            page_count = len(pdf_document)
            metadata['page_count'] = page_count
            
            # 全ページのテキストを抽出
            text = ""
            for page_num in range(page_count):
                page = pdf_document[page_num]
                text += page.get_text() + " "
                
            metadata['character_count'] = len(text)
            
            # PDFのメタデータを取得
            pdf_metadata = pdf_document.metadata
            if pdf_metadata:
                for key, value in pdf_metadata.items():
                    if value:  # 空でない値のみ保存
                        clean_key = key.lower()
                        metadata[f'pdf_{clean_key}'] = str(value)
            
            pdf_document.close()
            return text, metadata
            
        except Exception as e:
            # PDFの解析に失敗した場合
            print(f"PDF解析エラー: {str(e)}")
            return "", {"error": str(e)}
    
    else:
        # サポートされていないファイルタイプ
        return "", {"error": f"サポートされていないファイルタイプ: {content_type}"}

# 対応しているファイルタイプのリスト
SUPPORTED_FILE_TYPES = [
    'text/plain',
    'application/pdf'
]

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
    対応ファイル形式：テキスト、PDF
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
            if file.content_type.startswith('text/'):
                # テキストファイルの場合、最初の20文字をタイトルとして使用
                auto_title = extracted_text[:20] + ("..." if len(extracted_text) > 20 else "")
            elif file.content_type == 'application/pdf':
                # PDFファイルの場合、メタデータからタイトルを抽出
                if 'pdf_title' in file_metadata:
                    auto_title = file_metadata['pdf_title']
                else:
                    # PDFにタイトルがない場合はファイル名を使用
                    auto_title = file_name
        
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
        formatted_text = format(extracted_text, metadata_for_ai)
        
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
