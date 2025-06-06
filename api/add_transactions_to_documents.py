#!/usr/bin/env python3
"""
既存のドキュメントテーブルにトランザクション情報を追加するスクリプト
"""
import os
import sys
import boto3
import uuid
from datetime import datetime, timezone
import json

def main():
    try:
        print("💰 ドキュメントテーブルへのトランザクション情報追加開始ですわ～！")
        print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'Not set')}")
        
        # 指定されたドキュメントID
        document_ids = [
            '5f029e5c-cb8b-4f2e-9120-2b7cf718fac5',
            'a4b69f0e-5361-4568-9c18-cfb30ac649a2',
            'eae90aa0-d217-4bf8-a2dc-139017850272',
            'd541a0c7-dfaf-43e9-9d8c-7bab36e2c122',
            '9204b69b-97bf-4d97-b584-682e3c350b34',
        ]
        
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
        
        # 各ドキュメントIDに対してトランザクション情報を追加
        print(f"\n💰 トランザクション情報の追加を開始いたしますわ...")
        successful_updates = 0
        
        for i, doc_id in enumerate(document_ids):
            try:
                # まず既存のドキュメントを確認
                response = table.get_item(Key={'id': doc_id})
                
                if 'Item' not in response:
                    print(f"❌ ドキュメントID {doc_id} が存在しません")
                    continue
                
                existing_item = response['Item']
                print(f"📄 ドキュメント発見: {existing_item.get('title', 'N/A')}")
                
                # トランザクション情報を作成
                transaction_data = create_transaction_info(doc_id, i)
                
                # 既存のアイテムにトランザクション情報を追加
                # まず、transactionsリストを確認して適切に処理
                current_transactions = existing_item.get('transactions', [])
                updated_transactions = current_transactions + [transaction_data]
                current_total = existing_item.get('total_transactions', 0)
                
                update_expression = "SET transactions = :updated_transactions"
                update_expression += ", last_transaction_date = :timestamp"
                update_expression += ", total_transactions = :total_count"
                
                expression_attribute_values = {
                    ':updated_transactions': updated_transactions,
                    ':timestamp': transaction_data['created_at'],
                    ':total_count': current_total + 1
                }
                
                # ドキュメントを更新
                table.update_item(
                    Key={'id': doc_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values
                )
                
                print(f"✅ ドキュメントID {doc_id} にトランザクション情報追加成功！")
                print(f"   トランザクションID: {transaction_data['transaction_id']}")
                print(f"   種別: {transaction_data['type']} - ¥{transaction_data['amount']}")
                successful_updates += 1
                
            except Exception as e:
                print(f"❌ ドキュメントID {doc_id} の更新失敗: {e}")
        
        print(f"\n🎯 更新結果: {successful_updates}/{len(document_ids)} 件成功")
        
        if successful_updates > 0:
            print("\n📊 更新されたドキュメントを確認中...")
            
            # 更新されたドキュメントを確認
            for doc_id in document_ids[:3]:  # 最初の3件だけ確認
                try:
                    response = table.get_item(
                        Key={'id': doc_id},
                        ProjectionExpression='id, title, transactions, total_transactions, last_transaction_date'
                    )
                    
                    if 'Item' in response:
                        item = response['Item']
                        transactions = item.get('transactions', [])
                        total_count = item.get('total_transactions', 0)
                        
                        print(f"✅ {doc_id}:")
                        print(f"   タイトル: {item.get('title', 'N/A')}")
                        print(f"   トランザクション数: {total_count}")
                        
                        if transactions:
                            latest = transactions[-1]
                            print(f"   最新取引: {latest.get('type', 'N/A')} - ¥{latest.get('amount', 0)}")
                    else:
                        print(f"❌ {doc_id}: ドキュメントが見つからない")
                        
                except Exception as e:
                    print(f"❌ {doc_id} の確認でエラー: {e}")
        
        # 追加のトランザクション専用エントリも作成
        print(f"\n💎 トランザクション専用エントリも作成いたしますわ...")
        
        for i, doc_id in enumerate(document_ids):
            try:
                transaction_data = create_transaction_info(doc_id, i)
                transaction_id = transaction_data['transaction_id']
                
                # トランザクション専用エントリ
                transaction_entry = {
                    'id': f"transaction_{transaction_id}",
                    'type': 'transaction',
                    'transaction_id': transaction_id,
                    'document_id': doc_id,
                    'user_id': transaction_data['user_id'],
                    'transaction_type': transaction_data['type'],
                    'description': transaction_data['description'],
                    'amount': transaction_data['amount'],
                    'category': transaction_data['category'],
                    'status': transaction_data['status'],
                    'created_at': transaction_data['created_at'],
                    'updated_at': transaction_data['updated_at'],
                    'metadata': transaction_data['metadata']
                }
                
                table.put_item(Item=transaction_entry)
                print(f"✅ トランザクション専用エントリ作成: {transaction_id}")
                
            except Exception as e:
                print(f"❌ トランザクション専用エントリ作成失敗: {e}")
        
    except Exception as e:
        print(f"❌ エラーが発生しましたわ: {e}")
        import traceback
        traceback.print_exc()

def create_transaction_info(document_id: str, index: int) -> dict:
    """トランザクション情報を作成"""
    
    # 様々なトランザクションタイプとサンプルデータ
    transaction_types = [
        {
            "type": "document_upload",
            "description": "ドキュメントアップロード手数料",
            "amount": 100,
            "category": "service_fee"
        },
        {
            "type": "ai_analysis",
            "description": "AI文書分析サービス",
            "amount": 250,
            "category": "ai_service"
        },
        {
            "type": "storage_fee",
            "description": "ドキュメント保存料",
            "amount": 50,
            "category": "storage"
        },
        {
            "type": "search_premium",
            "description": "プレミアム検索機能",
            "amount": 300,
            "category": "premium_feature"
        },
        {
            "type": "export_service",
            "description": "ドキュメント出力サービス",
            "amount": 150,
            "category": "export"
        }
    ]
    
    # インデックスに基づいてトランザクションタイプを選択
    transaction_info = transaction_types[index % len(transaction_types)]
    
    current_time = datetime.now(timezone.utc)
    
    return {
        "transaction_id": str(uuid.uuid4()),
        "document_id": document_id,
        "user_id": f"user_{index + 1:03d}",
        "type": transaction_info["type"],
        "description": transaction_info["description"],
        "amount": transaction_info["amount"],
        "category": transaction_info["category"],
        "status": "completed",
        "created_at": current_time.isoformat(),
        "updated_at": current_time.isoformat(),
        "metadata": {
            "processing_time_ms": 1500 + (index * 100),
            "api_version": "v1.0",
            "source": "factify_api"
        }
    }

if __name__ == "__main__":
    main()
