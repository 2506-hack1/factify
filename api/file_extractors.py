"""
ファイル抽出モジュール
各種ファイルタイプからテキストとメタデータを抽出する機能を提供
"""
import io
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
from docx import Document
from bs4 import BeautifulSoup


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
        return _extract_plain_text(file_content, metadata)
    elif content_type == 'text/html':
        return _extract_html_content(file_content, metadata)
    elif content_type == 'application/pdf':
        return _extract_pdf_content(file_content, metadata)
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return _extract_docx_content(file_content, metadata)
    else:
        # サポートされていないファイルタイプ
        return "", {"error": f"サポートされていないファイルタイプ: {content_type}"}


def _extract_plain_text(file_content: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """プレーンテキストファイルの内容を抽出"""
    text = file_content.decode('utf-8')
    metadata['page_count'] = 1
    metadata['character_count'] = len(text)
    return text, metadata


def _extract_html_content(file_content: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """HTMLファイルの内容とメタデータを抽出"""
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


def _extract_pdf_content(file_content: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """PDFファイルの内容とメタデータを抽出"""
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


def _extract_docx_content(file_content: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Docxファイルの内容とメタデータを抽出"""
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
