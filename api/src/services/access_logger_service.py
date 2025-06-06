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


    def get_weekly_user_activity(self, days: int = 7) -> Dict:
        """
        過去N日間の日別ユニークユーザー数を取得する
        
        Parameters:
        -----------
        days : int
            遡る日数（デフォルト: 7日間）
            
        Returns:
        --------
        Dict
            日別ユニークユーザー統計
        """
        if not self.access_logs_table:
            return {}
            
        try:
            from datetime import datetime, timedelta
            
            # 現在時刻から指定日数分遡る
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 日別の統計を格納する辞書
            daily_stats = {}
            
            # 指定期間の全アクセスログを取得
            response = self.access_logs_table.scan(
                FilterExpression='#ts BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':start_date': start_date.isoformat(),
                    ':end_date': end_date.isoformat()
                }
            )
            
            access_logs = response.get('Items', [])
            
            # 日別にグループ化
            for log in access_logs:
                try:
                    # タイムスタンプから日付を抽出
                    log_date = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                    date_key = log_date.strftime('%Y-%m-%d')
                    
                    if date_key not in daily_stats:
                        daily_stats[date_key] = {
                            'date': date_key,
                            'unique_users': set(),
                            'total_accesses': 0
                        }
                    
                    daily_stats[date_key]['unique_users'].add(log['accessing_user_id'])
                    daily_stats[date_key]['total_accesses'] += 1
                    
                except Exception as e:
                    print(f"ログ処理エラー: {e}")
                    continue
            
            # setをcountに変換し、欠けている日付を補完
            result = []
            current_date = start_date
            
            while current_date <= end_date:
                date_key = current_date.strftime('%Y-%m-%d')
                
                if date_key in daily_stats:
                    result.append({
                        'date': date_key,
                        'unique_users': len(daily_stats[date_key]['unique_users']),
                        'total_accesses': daily_stats[date_key]['total_accesses']
                    })
                else:
                    # データがない日は0として追加
                    result.append({
                        'date': date_key,
                        'unique_users': 0,
                        'total_accesses': 0
                    })
                
                current_date += timedelta(days=1)
            
            return {
                'success': True,
                'period_days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'daily_stats': result,
                'total_unique_users': len(set(log['accessing_user_id'] for log in access_logs)),
                'total_accesses': len(access_logs)
            }
            
        except Exception as e:
            print(f"週間ユーザーアクティビティ取得エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'daily_stats': []
            }
    
    def generate_dummy_access_logs(self, num_days: int = 7, logs_per_day: int = 10) -> bool:
        """
        ダミーのアクセスログを生成する（テスト用）
        
        Parameters:
        -----------
        num_days : int
            過去何日分のデータを生成するか
        logs_per_day : int
            1日あたりのログ数
            
        Returns:
        --------
        bool
            生成の成功/失敗
        """
        if not self.access_logs_table:
            print("アクセスログテーブルが利用できません")
            return False
            
        try:
            import random
            from datetime import datetime, timedelta
            
            # 実在するユーザーID + ダミーユーザーIDリスト
            dummy_users = [
                'e7140a18-e051-702b-0341-77c46b86e717',  # 実在のユーザーID
                'user001', 'user002', 'user003', 'user004', 'user005',
                'user006', 'user007', 'user008', 'user009', 'user010'
            ]
            
            # 実在するドキュメントIDリスト（DynamoDBから取得した実際のID）
            dummy_documents = [
                '5f029e5c-cb8b-4f2e-9120-2b7cf718fac5',  # python_guide
                'a4b69f0e-5361-4568-9c18-cfb30ac649a2',  # ml_basics
                'eae90aa0-d217-4bf8-a2dc-139017850272',  # chat_history (2)
                'd541a0c7-dfaf-43e9-9d8c-7bab36e2c122',  # ml_basics
                '9204b69b-97bf-4d97-b584-682e3c350b34',  # aws_opensearch
                '93632a7c-bca4-49c8-a4cc-b9006d345b7c',  # python_guide
                '69645cd5-c6a0-4785-a98a-74b51224fd3c',  # aws_opensearch
                '225f4b5c-6de1-46bc-b5d3-1218e2fa3cba',  # ml_basics
                '8df4c38a-8261-4d1a-ac91-c9cacc7e2d27',  # aws_opensearch
                'f5629232-1b8a-42d6-9953-aa70e228b270'   # python_guide
            ]
            
            # ダミー検索クエリリスト
            dummy_queries = [
                'Python プログラミング', 'データ分析', 'AWS Lambda',
                '機械学習', 'Web開発', 'データベース設計',
                'API開発', 'TypeScript', 'React', 'FastAPI'
            ]
            
            generated_count = 0
            
            for day_offset in range(num_days):
                # 過去の日付を生成
                target_date = datetime.utcnow() - timedelta(days=day_offset)
                
                # その日のログ数をランダムに変動させる
                daily_logs = random.randint(max(1, logs_per_day - 5), logs_per_day + 5)
                
                for _ in range(daily_logs):
                    # ランダムな時間を生成
                    random_hour = random.randint(8, 22)
                    random_minute = random.randint(0, 59)
                    random_second = random.randint(0, 59)
                    
                    log_time = target_date.replace(
                        hour=random_hour,
                        minute=random_minute,
                        second=random_second,
                        microsecond=0
                    )
                    
                    # ランダムなアクセス情報を生成
                    accessing_user = random.choice(dummy_users)
                    document_owner = random.choice(dummy_users)
                    
                    # 自分のドキュメントへのアクセスは除外
                    while document_owner == accessing_user:
                        document_owner = random.choice(dummy_users)
                    
                    access_log_item = {
                        'transaction_id': str(uuid.uuid4()),
                        'timestamp': log_time.isoformat(),
                        'accessed_document_id': random.choice(dummy_documents),
                        'accessing_user_id': accessing_user,
                        'document_owner_id': document_owner,
                        'search_query': random.choice(dummy_queries),
                        'search_rank': random.randint(1, 10),
                        'access_type': 'search_result'
                    }
                    
                    # DynamoDBに記録
                    self.access_logs_table.put_item(Item=access_log_item)
                    generated_count += 1
                    
                print(f"日付 {target_date.strftime('%Y-%m-%d')}: {daily_logs}件のダミーログを生成")
                
            print(f"ダミーアクセスログ生成完了: 合計{generated_count}件")
            return True
            
        except Exception as e:
            print(f"ダミーデータ生成エラー: {e}")
            return False

# シングルトンインスタンス
access_logger_service = AccessLoggerService()
