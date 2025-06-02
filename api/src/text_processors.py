"""
テキスト処理モジュール
テキストの正規化とAI用フォーマット化を担当
"""
import re
from typing import Dict, Any


def clean_text(raw_text: str) -> str:
    """
    テキストの正規化を行う
    
    Parameters:
    -----------
    raw_text : str
        正規化前のテキスト
        
    Returns:
    --------
    str
        正規化されたテキスト
    """
    # 全角スペースやタブを半角スペースに変換
    text = raw_text.replace("\u3000", " ").replace("\t", " ")
    # 改行もスペースに置換
    text = text.replace("\r", " ").replace("\n", " ")
    # 複数スペースを1つにする
    text = re.sub(r" +", " ", text)
    return text.strip()


def format_for_ai(content: str, metadata: Dict[str, Any]) -> str:
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

    elif metadata.get('file_type') == 'docx':
        if 'paragraph_count' in metadata:
            formatted_text += f"- 段落数: {metadata['paragraph_count']}\n"
            
        # Docx特有のメタデータを追加
        for key, value in metadata.items():
            if key.startswith('docx_') and key != 'docx_title' and value:
                formatted_text += f"- {key[5:].capitalize()}: {value}\n"
                
    elif metadata.get('file_type') == 'html':
        if 'html_tags_count' in metadata:
            formatted_text += f"- HTMLタグ数: {metadata['html_tags_count']}\n"
            
        # HTML特有のメタデータを追加
        for key, value in metadata.items():
            if key.startswith('html_') and key != 'html_title' and value:
                formatted_text += f"- {key[5:].capitalize()}: {value}\n"
    
    # 文字数
    if 'character_count' in metadata:
        formatted_text += f"- 文字数: {metadata['character_count']}\n"
        
    # 作成日時
    if 'uploaded_at' in metadata:
        formatted_text += f"- アップロード日時: {metadata['uploaded_at']}\n"
    
    return formatted_text
