"""
アプリケーション設定ファイル
AWS リソースの設定や定数を管理します
"""
import os

# AWSリソース設定（環境変数から取得、デフォルト値も設定）
REGION_NAME = os.getenv("REGION_NAME", "ap-northeast-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "factify-dynamodb-table")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "factify-s3-bucket")

# 対応しているファイルタイプのリスト
SUPPORTED_FILE_TYPES = [
    'text/plain',
    'text/html',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
