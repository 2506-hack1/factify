#!/usr/bin/env python3
"""
実際のユーザーIDでインセンティブデータを作成するスクリプト
"""
import os
import sys
import boto3
import uuid
from datetime import datetime, timezone
import json

def main():
    try:
        print("💎 実際のユーザーIDでインセンティブデータ作成開始ですわ～！")
        print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'Not set')}")
        
        # 実際のユーザーID
        real_user_id = "e7140a18-e051-702b-0341-77c46b86e717"
        
        # 指定されたドキュメントID
        document_ids = [
            '5f029e5c-cb8b-4f2e-9120-2b7cf718fac5',
            'a4b69f0e-5361-4568-9c18-cfb30ac649a2',
            'eae90aa0-d217-4bf8-a2dc-139017850272',
            'd541a0c7-dfaf-43e9-9d8c-7bab36e2c122',
            '9204b69b-97bf-4d97-b584-682e3c350b34',
        ]
        
        print(f"👤 実際のユーザーID: {real_user_id}")
        print(f"📄 対象ドキュメント数: {len(document_ids)}件")
        
        # DynamoDBクライアント初期化
        dynamodb = boto3.resource('dynamodb')
        region = os.environ.get('AWS_REGION', 'ap-northeast-1')
        
        # 既存のドキュメントテーブルを使用
        table_name = "factify-dynamodb-table-471112951833-ap-northeast-1"
        
        try:
            table = dynamodb.Table(table_name)
            table.load()
            print(f"✅ ドキュメントテーブル発見: {table_name}")
        except Exception as e:
            print(f"❌ テーブル {table_name} にアクセスできません: {e}")
            return
        
        # まず、指定されたドキュメントのowner_user_idを実際のユーザーIDに変更
        print(f"\n📝 ドキュメントのowner_user_idを更新中...")
        
        for doc_id in document_ids:
            try:
                # 既存のドキュメントを確認
                response = table.get_item(Key={'id': doc_id})
                
                if 'Item' not in response:
                    print(f"❌ ドキュメントID {doc_id} が存在しません")
                    continue
                
                existing_item = response['Item']
                current_owner = existing_item.get('owner_user_id', 'N/A')
                
                # owner_user_idを実際のユーザーIDに更新
                table.update_item(
                    Key={'id': doc_id},
                    UpdateExpression="SET owner_user_id = :user_id",
                    ExpressionAttributeValues={
                        ':user_id': real_user_id
                    }
                )
                
                print(f"✅ {doc_id}: owner_user_id更新 ({current_owner} → {real_user_id[:8]}...)")
                
            except Exception as e:
                print(f"❌ ドキュメントID {doc_id} の更新失敗: {e}")
        
        # インセンティブデータを作成
        print(f"\n🎯 インセンティブデータを作成中...")
        
        # 現在の期間（YYYY-MM形式）
        current_period = datetime.now().strftime('%Y-%m')
        
        # アクセスログエントリを作成（他のユーザーからのアクセスをシミュレート）
        access_logs = []
        accessing_users = [
            "user_001_visitor",
            "user_002_visitor", 
            "user_003_visitor",
            "user_004_visitor",
            "user_005_visitor"
        ]
        
        total_access_count = 0
        document_access_details = {}
        
        for i, doc_id in enumerate(document_ids):
            # 各ドキュメントに対して複数のアクセスを生成
            access_count = 3 + (i * 2)  # 3, 5, 7, 9, 11回のアクセス
            unique_users = min(len(accessing_users), access_count)
            
            total_access_count += access_count
            document_access_details[doc_id] = {
                "access_count": access_count,
                "unique_users": unique_users
            }
            
            # アクセスログエントリを作成
            for j in range(access_count):
                user_index = j % len(accessing_users)
                accessing_user = accessing_users[user_index]
                
                access_log = {
                    'id': f"access_log_{uuid.uuid4()}",
                    'type': 'access_log',
                    'transaction_id': str(uuid.uuid4()),
                    'accessed_document_id': doc_id,
                    'accessing_user_id': accessing_user,
                    'document_owner_id': real_user_id,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'search_query': f"検索クエリ{j+1}",
                    'search_rank': j + 1,
                    'access_type': 'search_result',
                    'period': current_period
                }
                
                access_logs.append(access_log)
        
        # アクセスログをDynamoDBに保存
        print(f"💾 アクセスログを保存中... ({len(access_logs)}件)")
        
        for log in access_logs:
            try:
                table.put_item(Item=log)
            except Exception as e:
                print(f"❌ アクセスログ保存失敗: {e}")
        
        # インセンティブ集計データを作成
        unique_users_count = len(accessing_users)
        total_incentive_points = total_access_count + (unique_users_count * 5 * len(document_ids))
        
        incentive_data = {
            'id': f"incentive_{real_user_id}_{current_period}",
            'type': 'incentive_summary',
            'owner_user_id': real_user_id,
            'period': current_period,
            'total_access_count': total_access_count,
            'unique_users_count': unique_users_count,
            'total_incentive_points': total_incentive_points,
            'document_access_details': document_access_details,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # インセンティブデータを保存
        print(f"🎯 インセンティブ集計データを保存中...")
        
        try:
            table.put_item(Item=incentive_data)
            print(f"✅ インセンティブデータ保存成功！")
            print(f"   ユーザーID: {real_user_id}")
            print(f"   期間: {current_period}")
            print(f"   総アクセス数: {total_access_count}")
            print(f"   ユニークユーザー数: {unique_users_count}")
            print(f"   総ポイント: {total_incentive_points}")
        except Exception as e:
            print(f"❌ インセンティブデータ保存失敗: {e}")
        
        # 結果を表示
        print(f"\n📊 作成されたデータ:")
        print(f"  📄 ドキュメント: {len(document_ids)}件")
        print(f"  📈 アクセスログ: {len(access_logs)}件")
        print(f"  🎯 インセンティブポイント: {total_incentive_points}pt")
        
        print(f"\n📋 ドキュメント別詳細:")
        for doc_id, details in document_access_details.items():
            revenue = details['access_count'] + (details['unique_users'] * 5)
            print(f"  {doc_id[:8]}...: {details['access_count']}回アクセス, {details['unique_users']}人, {revenue}pt")
        
        print(f"\n✨ Analyticsページで確認してくださいませ〜！")
        
    except Exception as e:
        print(f"❌ エラーが発生しましたわ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
