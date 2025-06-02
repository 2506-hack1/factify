"""
AWS サービス操作モジュール
S3とDynamoDB操作を担当
"""
import boto3
from typing import Dict, Any
from config import REGION_NAME, DYNAMODB_TABLE_NAME, S3_BUCKET_NAME


class AWSServices:
    """AWS サービス操作クラス"""
    
    def __init__(self):
        """AWS クライアントを初期化"""
        self.s3_client = boto3.client('s3', region_name=REGION_NAME)
        self.dynamodb_client = boto3.resource('dynamodb', region_name=REGION_NAME)
        self.table = self.dynamodb_client.Table(DYNAMODB_TABLE_NAME)
    
    def upload_to_s3(self, content: str, s3_key: str) -> None:
        """
        S3にテキストコンテンツをアップロードする
        
        Parameters:
        -----------
        content : str
            アップロードするテキストコンテンツ
        s3_key : str
            S3オブジェクトキー
        """
        self.s3_client.put_object(
            Body=content.encode('utf-8'),
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            ContentType='text/plain; charset=utf-8'
        )
    
    def save_to_dynamodb(self, item: Dict[str, Any]) -> None:
        """
        DynamoDBにアイテムを保存する
        
        Parameters:
        -----------
        item : Dict[str, Any]
            保存するアイテム辞書
        """
        self.table.put_item(Item=item)
    
    def get_s3_client(self):
        """S3クライアントを取得（下位互換性のため）"""
        return self.s3_client
    
    def get_dynamodb_table(self):
        """DynamoDBテーブルを取得（下位互換性のため）"""
        return self.table


# シングルトンインスタンス
aws_services = AWSServices()
