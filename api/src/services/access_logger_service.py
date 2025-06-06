"""
アクセス履歴記録サービス
検索結果の参照をトラッキングしてインセンティブ計算の基盤とする
"""
import uuid
import boto3
from datetime import datetime
from typing import Dict, List, Optional
from ..config import AWS_REGION, DYNAMODB_TABLE_NAME


class AccessLoggerService:
    """アクセス履歴記録とインセンティブ管理サービス"""
    
    def __init__(self):
        # DynamoDBクライアントの初期化
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        
        # テーブル名を動的に生成（環境に応じて）
        account_id = boto3.client('sts').get_caller_identity()['Account']
        self.access_logs_table_name = f"factify-access-logs-{account_id}-{AWS_REGION}"
        self.incentive_summary_table_name = f"factify-incentive-summary-{account_id}-{AWS_REGION}"
        
        # テーブル参照を取得
        try:
            self.access_logs_table = self.dynamodb.Table(self.access_logs_table_name)
            self.incentive_summary_table = self.dynamodb.Table(self.incentive_summary_table_name)
        except Exception as e:
            print(f"DynamoDBテーブル接続エラー: {e}")
            self.access_logs_table = None
            self.incentive_summary_table = None
    
    def log_search_access(self, 
                         accessed_documents: List[Dict], 
                         accessing_user_id: str, 
                         search_query: str) -> bool:
        """
        検索結果のアクセスを記録する
        
        Parameters:
        -----------
        accessed_documents : List[Dict]
            アクセスされたドキュメントのリスト
        accessing_user_id : str
            検索を実行したユーザーID
        search_query : str
            検索クエリ
            
        Returns:
        --------
        bool
            記録の成功/失敗
        """
        if not self.access_logs_table:
            print("アクセスログテーブルが利用できません")
            return False
            
        try:
            current_time = datetime.utcnow().isoformat()
            
            # 各ドキュメントのアクセスを記録
            for rank, document in enumerate(accessed_documents, 1):
                transaction_id = str(uuid.uuid4())
                document_owner_id = document.get('user_id', 'unknown')
                
                # 自分のドキュメントへのアクセスは記録しない（インセンティブ対象外）
                if document_owner_id == accessing_user_id:
                    continue
                
                access_log_item = {
                    'transaction_id': transaction_id,
                    'timestamp': current_time,
                    'accessed_document_id': document.get('id'),
                    'accessing_user_id': accessing_user_id,
                    'document_owner_id': document_owner_id,
                    'search_query': search_query,
                    'search_rank': rank,
                    'access_type': 'search_result'
                }
                
                # DynamoDBに非同期で記録
                self.access_logs_table.put_item(Item=access_log_item)
                
            print(f"アクセス履歴記録完了: {len(accessed_documents)}件")
            return True
            
        except Exception as e:
            print(f"アクセス履歴記録エラー: {e}")
            return False
    
    def get_user_access_logs(self, 
                           user_id: str, 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None, 
                           limit: int = 100) -> List[Dict]:
        """
        ユーザーのアクセス履歴を取得する
        
        Parameters:
        -----------
        user_id : str
            ユーザーID
        start_date : str, optional
            開始日時 (ISO形式)
        end_date : str, optional
            終了日時 (ISO形式)
        limit : int
            取得件数制限
            
        Returns:
        --------
        List[Dict]
            アクセス履歴のリスト
        """
        if not self.access_logs_table:
            return []
            
        try:
            # GSIを使用してユーザー別検索
            response = self.access_logs_table.query(
                IndexName='UserAccessIndex',
                KeyConditionExpression='accessing_user_id = :user_id',
                ExpressionAttributeValues={
                    ':user_id': user_id
                },
                ScanIndexForward=False,  # 降順（最新から）
                Limit=limit
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"アクセス履歴取得エラー: {e}")
            return []
    
    def get_document_access_stats(self, 
                                 document_id: str, 
                                 period_days: int = 30) -> Dict:
        """
        ドキュメントのアクセス統計を取得する
        
        Parameters:
        -----------
        document_id : str
            ドキュメントID
        period_days : int
            統計期間（日数）
            
        Returns:
        --------
        Dict
            アクセス統計情報
        """
        if not self.access_logs_table:
            return {}
            
        try:
            # GSIを使用してドキュメント別検索
            response = self.access_logs_table.query(
                IndexName='DocumentAccessIndex',
                KeyConditionExpression='accessed_document_id = :doc_id',
                ExpressionAttributeValues={
                    ':doc_id': document_id
                }
            )
            
            access_logs = response.get('Items', [])
            
            # 統計を計算
            total_access = len(access_logs)
            unique_users = len(set(log['accessing_user_id'] for log in access_logs))
            
            return {
                'document_id': document_id,
                'total_access_count': total_access,
                'unique_users_count': unique_users,
                'access_logs': access_logs[:10]  # 最新10件のみ
            }
            
        except Exception as e:
            print(f"ドキュメント統計取得エラー: {e}")
            return {}
    
    def calculate_incentive_points(self, 
                                  owner_user_id: str, 
                                  period_month: str) -> Dict:
        """
        指定期間のインセンティブポイントを計算する
        
        Parameters:
        -----------
        owner_user_id : str
            ドキュメント所有者のユーザーID
        period_month : str
            対象月 (YYYY-MM形式)
            
        Returns:
        --------
        Dict
            インセンティブ計算結果
        """
        if not self.access_logs_table:
            return {}
            
        try:
            # 指定月のアクセス履歴を取得
            start_date = f"{period_month}-01T00:00:00"
            end_date = f"{period_month}-31T23:59:59"
            
            response = self.access_logs_table.scan(
                FilterExpression='document_owner_id = :owner_id AND #ts BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':owner_id': owner_user_id,
                    ':start_date': start_date,
                    ':end_date': end_date
                }
            )
            
            access_logs = response.get('Items', [])
            
            # インセンティブポイント計算
            total_access = len(access_logs)
            unique_users = len(set(log['accessing_user_id'] for log in access_logs))
            
            # ポイント計算ロジック（カスタマイズ可能）
            base_points = total_access * 1  # 基本：1アクセス = 1ポイント
            unique_user_bonus = unique_users * 5  # ボーナス：ユニークユーザー1人 = 5ポイント
            total_points = base_points + unique_user_bonus
            
            # ドキュメント別詳細
            document_details = {}
            for log in access_logs:
                doc_id = log['accessed_document_id']
                if doc_id not in document_details:
                    document_details[doc_id] = {
                        'access_count': 0,
                        'unique_users': set()
                    }
                document_details[doc_id]['access_count'] += 1
                document_details[doc_id]['unique_users'].add(log['accessing_user_id'])
            
            # set を count に変換
            for doc_id in document_details:
                document_details[doc_id]['unique_users'] = len(document_details[doc_id]['unique_users'])
            
            return {
                'owner_user_id': owner_user_id,
                'period': period_month,
                'total_access_count': total_access,
                'unique_users_count': unique_users,
                'total_incentive_points': total_points,
                'document_access_details': document_details
            }
            
        except Exception as e:
            print(f"インセンティブ計算エラー: {e}")
            return {}
    
    def save_incentive_summary(self, incentive_data: Dict) -> bool:
        """
        インセンティブ集計結果を保存する
        
        Parameters:
        -----------
        incentive_data : Dict
            インセンティブデータ
            
        Returns:
        --------
        bool
            保存の成功/失敗
        """
        if not self.incentive_summary_table:
            return False
            
        try:
            self.incentive_summary_table.put_item(Item=incentive_data)
            print(f"インセンティブ集計保存完了: {incentive_data['owner_user_id']} - {incentive_data['period']}")
            return True
            
        except Exception as e:
            print(f"インセンティブ集計保存エラー: {e}")
            return False


# シングルトンインスタンス
access_logger_service = AccessLoggerService()
