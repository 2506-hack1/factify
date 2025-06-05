"""
メタデータ処理モジュール
ファイルメタデータの処理とタイトル自動生成を担当
"""
import os
from typing import Dict, Any, Optional


def generate_auto_title(title: str, content_type: str, extracted_text: str, 
                       file_metadata: Dict[str, Any], file_name: str) -> str:
    """
    ファイルタイプに応じて自動的にタイトルを生成する
    
    Parameters:
    -----------
    title : str
        ユーザーが入力したタイトル
    content_type : str
        ファイルのMIMEタイプ
    extracted_text : str
        抽出されたテキスト
    file_metadata : Dict[str, Any]
        ファイルから抽出されたメタデータ
    file_name : str
        ファイル名（拡張子なし）
        
    Returns:
    --------
    str
        生成されたタイトル
    """
    # ユーザーがタイトルを指定した場合はそれを使用
    if title and title.strip():
        return title
    
    # ファイルタイプに応じてタイトルを生成
    if content_type == 'text/plain':
        # プレーンテキストファイルの場合、最初の20文字をタイトルとして使用
        return extracted_text[:20] + ("..." if len(extracted_text) > 20 else "")
        
    elif content_type == 'text/html':
        # HTMLファイルの場合、メタデータからタイトルを抽出
        if 'html_title' in file_metadata:
            return file_metadata['html_title']
        else:
            # HTMLにタイトルがない場合は最初の20文字を使用
            return extracted_text[:20] + ("..." if len(extracted_text) > 20 else "") if extracted_text else file_name
            
    elif content_type == 'application/pdf':
        # PDFファイルの場合、メタデータからタイトルを抽出
        if 'pdf_title' in file_metadata:
            return file_metadata['pdf_title']
        else:
            # PDFにタイトルがない場合はファイル名を使用
            return file_name
            
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        # Docxファイルの場合、メタデータからタイトルを抽出
        if 'docx_title' in file_metadata:
            return file_metadata['docx_title']
        else:
            # Docxにタイトルがない場合は最初の20文字を使用
            return extracted_text[:20] + ("..." if len(extracted_text) > 20 else "") if extracted_text else file_name
    
    # デフォルトはファイル名を使用
    return file_name


def parse_filename(original_filename: str) -> tuple[str, str]:
    """
    ファイル名を解析して名前と拡張子に分割する
    
    Parameters:
    -----------
    original_filename : str
        元のファイル名
        
    Returns:
    --------
    tuple[str, str]
        (ファイル名（拡張子なし）, 拡張子（ピリオドなし）)
    """
    file_name_parts = os.path.splitext(original_filename)
    file_name = file_name_parts[0]  # 拡張子なしのファイル名
    file_extension = file_name_parts[1].lower().lstrip('.')  # 拡張子（ピリオドなし）
    return file_name, file_extension


def create_metadata_for_ai(auto_title: str, description: str, file_extension: str, 
                          file_name: str, uploaded_at: str, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI用のメタデータ辞書を作成する
    
    Parameters:
    -----------
    auto_title : str
        自動生成されたタイトル
    description : str
        ファイルの説明
    file_extension : str
        ファイル拡張子
    file_name : str
        ファイル名（拡張子なし）
    uploaded_at : str
        アップロード日時
    file_metadata : Dict[str, Any]
        ファイルから抽出されたメタデータ
        
    Returns:
    --------
    Dict[str, Any]
        AI用のメタデータ辞書
    """
    return {
        "title": auto_title,
        "description": description or "",
        "file_type": file_extension,
        "file_name": file_name,
        "uploaded_at": uploaded_at,
        **file_metadata
    }


def create_dynamodb_item(file_id: str, s3_key: str, file_name: str, file_extension: str,
                        uploaded_at: str, auto_title: str, description: str, 
                        content_type: str, file_metadata: Dict[str, Any], 
                        formatted_text: str, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    DynamoDB用のアイテム辞書を作成する
    
    Parameters:
    -----------
    file_id : str
        ファイルID
    s3_key : str
        S3オブジェクトキー
    file_name : str
        ファイル名（拡張子なし）
    file_extension : str
        ファイル拡張子
    uploaded_at : str
        アップロード日時
    auto_title : str
        自動生成されたタイトル
    description : str
        ファイルの説明
    content_type : str
        ファイルのMIMEタイプ
    file_metadata : Dict[str, Any]
        ファイルから抽出されたメタデータ
    formatted_text : str
        AI用に整形されたテキスト
    user_info : Optional[Dict[str, Any]]
        ユーザー情報（認証されている場合のみ）
        
    Returns:
    --------
    Dict[str, Any]
        DynamoDB用のアイテム辞書
    """
    item = {
        "id": file_id,
        "s3_key": s3_key,
        "file_name": file_name,
        "file_type": file_extension,
        "uploaded_at": uploaded_at,
        "title": auto_title,
        "description": description or "",
        "content_type": content_type,
        "extracted_metadata": file_metadata,
        "formatted_text": formatted_text
    }
    
    # ユーザー情報が提供されている場合は追加
    if user_info:
        item.update({
            "user_id": user_info.get("user_id"),
            "user_email": user_info.get("email"),
            "user_username": user_info.get("username"),
            "is_authenticated": True
        })
    else:
        item["is_authenticated"] = False
    
    return item
