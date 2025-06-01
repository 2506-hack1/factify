from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz             # PDF用（PyMuPDF）
import docx             # Word用（python-docx）
import openpyxl         # Excel用
import io
import re
import boto3
import uuid
import logging
from botocore.exceptions import BotoCoreError, ClientError

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# テキストの正規化を行う
def clean_text(raw_text: str) -> str:
    # 全角スペースやタブを半角スペースに変換
    text = raw_text.replace("\u3000", " ").replace("\t", " ")
    # 改行もスペースに置換
    text = text.replace("\r", " ").replace("\n", " ")
    # 複数スペースを1つにする
    text = re.sub(r" +", " ", text)
    return text.strip()


# DynamoDBのリソースとテーブル設定
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
table = dynamodb.Table('Documents')

# DynamoDBに格納する関数
def save_to_dynamodb(item_id: str, filename: str, content: str):
    item = {
        'id': item_id,
        'filename': filename,
        'content': content
    }
    try:
        logger.debug(f"DynamoDB保存開始 id={item_id}")
        table.put_item(Item=item)
        logger.info(f"DynamoDBに保存成功: id={item_id}, filename={filename}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"DynamoDB保存失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DynamoDB保存失敗: {str(e)}")


@app.post("/upload/file")
async def extract_text(file: UploadFile = File(...)):
    logger.debug("1: ファイルアップロード受信")
    contents = await file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower()
    logger.debug(f"2: 拡張子は {ext}")

    try:
        if ext == "pdf":
            logger.debug("3: PDF処理開始")
            doc = fitz.open(stream=contents, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)

        elif ext == "docx":
            logger.debug("4: Word処理開始")
            word_doc = docx.Document(io.BytesIO(contents))
            text = "\n".join(p.text for p in word_doc.paragraphs)

        elif ext in ("xls", "xlsx"):
            logger.debug("5: Excel処理開始")
            workbook = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
            rows = []
            for sheet in workbook.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    rows.append("\t".join(str(cell) if cell is not None else "" for cell in row))
            text = "\n".join(rows)

        else:
            logger.warning("6: 未対応のファイル形式")
            raise HTTPException(status_code=400, detail="サポートされていない file typeです。")

        logger.debug("7: テキスト正規化")
        cleaned_text = clean_text(text)

        item_id = str(uuid.uuid4())
        logger.debug(f"8: 保存処理開始 id={item_id}")
        save_to_dynamodb(item_id, file.filename, cleaned_text)
        logger.debug("9: 保存処理終了")

    except Exception as e:
        logger.exception("例外発生:")
        raise HTTPException(status_code=500, detail=f"テキスト抽出に失敗しました: {str(e)}")

    return {
        'id': item_id,
        'filename': file.filename,
        'content': cleaned_text,
        'message': 'DynamoDBに保存しました'
    }
