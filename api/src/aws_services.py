"""
AWS サービス操作モジュール
S3とDynamoDB操作を担当
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, List
from .config import REGION_NAME, DYNAMODB_TABLE_NAME, S3_BUCKET_NAME


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
    
    def upload_file_to_s3(self, file_content: bytes, s3_key: str, content_type: str) -> None:
        """
        S3にファイルをアップロードする（バイナリデータ用）
        
        Parameters:
        -----------
        file_content : bytes
            アップロードするファイルコンテンツ
        s3_key : str
            S3オブジェクトキー
        content_type : str
            ファイルのMIMEタイプ
        """
        self.s3_client.put_object(
            Body=file_content,
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            ContentType=content_type
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
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        DynamoDBからドキュメントを検索する
        
        Parameters:
        -----------
        query : str
            検索クエリ
        max_results : int
            返す最大結果数
            
        Returns:
        --------
        List[Dict]
            検索結果のリスト
        """
        try:
            # DynamoDBでスキャンして検索
            response = self.table.scan(
                FilterExpression=Attr('formatted_text').contains(query),
            )
            
            items = response.get('Items', [])
            
            # 結果を制限
            limited_items = items[:max_results]
            
            # 検索結果を整形
            search_results = []
            for item in limited_items:
                result = {
                    'file_id': item.get('file_id'),
                    'filename': item.get('filename'),
                    'language': item.get('language'),
                    'processed_at': item.get('processed_at'),
                    'file_type': item.get('file_type'),
                    's3_key': item.get('s3_key'),
                    # formatted_textの一部を返す（プレビュー用）
                    'preview': item.get('formatted_text', '')[:200] + '...' if len(item.get('formatted_text', '')) > 200 else item.get('formatted_text', '')
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            print(f"検索エラー: {e}")
            return []


# シングルトンインスタンス
aws_services = AWSServices()
