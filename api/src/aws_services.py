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
    
    def search_documents(self, query: str, max_results: int = 5, user_id: str = None) -> List[Dict]:
        """
        DynamoDBからドキュメントを検索する
        
        Parameters:
        -----------
        query : str
            検索クエリ
        max_results : int
            返す最大結果数
        user_id : str
            ユーザーID（指定した場合、そのユーザーのファイルのみを検索）
            
        Returns:
        --------
        List[Dict]
            検索結果のリスト
        """
        try:
            # ベースのフィルタ式を作成
            filter_expression = Attr('formatted_text').contains(query)
            
            # ユーザーIDが指定されている場合、ユーザー固有のフィルタを追加
            if user_id:
                user_filter = Attr('user_id').eq(user_id)
                filter_expression = filter_expression & user_filter
            
            # DynamoDBでスキャンして検索
            response = self.table.scan(
                FilterExpression=filter_expression,
            )
            
            items = response.get('Items', [])
            print(f"検索結果: {len(items)}件のアイテムが見つかりました")
            
            # デバッグ用：最初のアイテムの構造を出力
            if items:
                print(f"最初のアイテム構造: {list(items[0].keys())}")
                print(f"最初のアイテムの一部: {dict(list(items[0].items())[:3])}")
            
            # 結果を制限
            limited_items = items[:max_results]
            
            # 検索結果を整形（DynamoDBスキーマに基づく正確なマッピング）
            search_results = []
            for item in limited_items:
                # DynamoDBから取得した実際のフィールドをそのまま使用
                result = {
                    # SearchResultモデルに必要なフィールド
                    'id': item['id'],  # UUID
                    's3_key': item['s3_key'],  # string
                    'file_name': item['file_name'],  # string
                    'file_type': item['file_type'],  # string（拡張子）
                    'formatted_text': item['formatted_text'],  # string
                    'uploaded_at': item['uploaded_at'],  # date (ISO 8601)
                    'title': item['title'],  # string
                    'description': item['description'],  # string
                    'extracted_metadata': item['extracted_metadata'],  # JSON
                    # プレビュー用（オプション）
                    'preview': item['formatted_text'][:200] + '...' if len(item['formatted_text']) > 200 else item['formatted_text']
                }
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            print(f"検索エラー: {e}")
            print(f"エラーの詳細: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


# シングルトンインスタンス
aws_services = AWSServices()
