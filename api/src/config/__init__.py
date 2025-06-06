"""
Configuration package for the API
"""
import os

# AWSリソース設定（環境変数から取得、デフォルト値も設定）
REGION_NAME = os.getenv("REGION_NAME", "ap-northeast-1")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")  # access_logger_service用
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "factify-dynamodb-table-471112951833-ap-northeast-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "factify-s3-bucket-471112951833-ap-northeast-1")

# OpenSearch設定（AWS OpenSearchサービス）
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "https://search-factify-search-demo-zv7xz3e4q2wwgm2eer2aoirt2e.ap-northeast-1.es.amazonaws.com")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "admin")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "TempPassword123!")

# 対応しているファイルタイプのリスト
SUPPORTED_FILE_TYPES = [
    'text/plain',
    'text/html',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

# cognito_config.pyからCognito設定をインポート  
from .cognito_config import COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID, AWS_DEFAULT_REGION

# すべてを再エクスポート
__all__ = [
    'SUPPORTED_FILE_TYPES',
    'REGION_NAME', 
    'AWS_REGION',
    'DYNAMODB_TABLE_NAME',
    'S3_BUCKET_NAME',
    'OPENSEARCH_ENDPOINT',
    'COGNITO_REGION',
    'COGNITO_USER_POOL_ID', 
    'COGNITO_CLIENT_ID',
    'AWS_DEFAULT_REGION'
]
