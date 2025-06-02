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

app = FastAPI()

# AWS クライアント初期化
s3_client = boto3.client('s3', region_name=REGION_NAME)
dynamodb_client = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)

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
    
    if content_type == 'text/plain':
        # プレーンテキストファイルの場合
        text = file_content.decode('utf-8')
        metadata['page_count'] = 1
        metadata['character_count'] = len(text)
        return text, metadata
        
    elif content_type == 'text/html':
        # HTMLファイルの場合
        try:
            # HTMLコンテンツをデコード
            html_content = file_content.decode('utf-8')
            
            # Beautiful Soupでパース
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # メタデータを抽出
            title_tag = soup.find('title')
            if title_tag:
                metadata['html_title'] = title_tag.get_text().strip()
            
            # メタタグからメタデータを抽出
            meta_description = soup.find('meta', attrs={'name': 'description'})
            if meta_description and meta_description.get('content'):
                metadata['html_description'] = meta_description.get('content')
                
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                metadata['html_keywords'] = meta_keywords.get('content')
                
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author and meta_author.get('content'):
                metadata['html_author'] = meta_author.get('content')
            
            # テキストコンテンツを抽出（スクリプトやスタイルは除外）
            for script in soup(["script", "style"]):
                script.decompose()
            
            # テキストを抽出
            text = soup.get_text()
            
            # 行の正規化
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            metadata['character_count'] = len(text)
            metadata['html_tags_count'] = len(soup.find_all())
            
            return text, metadata
            
        except Exception as e:
            # HTMLの解析に失敗した場合
            print(f"HTML解析エラー: {str(e)}")
            return "", {"error": str(e)}
        
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
    
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        # Docxファイルの場合
        try:
            # python-docxを使用してDocxファイルを開く
            docx_file = io.BytesIO(file_content)
            document = Document(docx_file)
            
            # 全段落のテキストを抽出
            text = ""
            paragraph_count = 0
            for paragraph in document.paragraphs:
                if paragraph.text.strip():  # 空でない段落のみ
                    text += paragraph.text + "\n"
                    paragraph_count += 1
            
            metadata['paragraph_count'] = paragraph_count
            metadata['character_count'] = len(text)
            
            # Docxのメタデータを取得
            if document.core_properties:
                core_props = document.core_properties
                if core_props.title:
                    metadata['docx_title'] = str(core_props.title)
                if core_props.author:
                    metadata['docx_author'] = str(core_props.author)
                if core_props.subject:
                    metadata['docx_subject'] = str(core_props.subject)
                if core_props.created:
                    metadata['docx_created'] = str(core_props.created)
                if core_props.modified:
                    metadata['docx_modified'] = str(core_props.modified)
            
            return text, metadata
            
        except Exception as e:
            # Docxの解析に失敗した場合
            print(f"Docx解析エラー: {str(e)}")
            return "", {"error": str(e)}
    
    else:
        # サポートされていないファイルタイプ
        return "", {"error": f"サポートされていないファイルタイプ: {content_type}"}



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
