#!/usr/bin/env python3
"""
指定されたドキュメントIDに対してトランザクションを挿入するスクリプト
"""
import os
import sys
import boto3
import uuid
from datetime import datetime
import json

def main():
    try:
        print("💰 トランザクション挿入開始ですわ～！")
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
        
        # トランザクションテーブル名を推定
        possible_transaction_table_names = [
            f"factify-transactions-{region}",
            "factify-transactions",
            f"factify-transaction-table-471112951833-{region}",
            "factify-transaction-table"
        ]
        
        transaction_table = None
        transaction_table_name = None
        
        # トランザクションテーブルを探す
        for name in possible_transaction_table_names:
            try:
                test_table = dynamodb.Table(name)
                test_table.load()
                transaction_table = test_table
                transaction_table_name = name
                print(f"✅ トランザクションテーブル発見: {name}")
                break
            except Exception as e:
                print(f"❌ テーブル {name} が見つからない: {str(e)[:50]}...")
                continue
        
        if not transaction_table:
            print("❌ トランザクションテーブルが見つかりませんでした")
            
            # 利用可能なテーブル一覧を表示
            print("\n📋 利用可能なテーブル一覧:")
            client = boto3.client('dynamodb')
            tables = client.list_tables()
            for table_name in tables.get('TableNames', []):
                print(f"  - {table_name}")
            
            # テーブルが見つからない場合、仮想的なトランザクションデータを作成
            print("\n💡 テーブルが見つからないため、トランザクションデータの構造例を表示いたしますわ:")
            for i, doc_id in enumerate(document_ids):
                transaction_data = create_sample_transaction(doc_id, i)
                print(f"\n📝 ドキュメントID: {doc_id}")
                print(json.dumps(transaction_data, indent=2, ensure_ascii=False))
            return
        
        # 各ドキュメントIDに対してトランザクションを作成
        print(f"\n💰 トランザクション挿入を開始いたしますわ...")
        successful_inserts = 0
        
        for i, doc_id in enumerate(document_ids):
            try:
                transaction_data = create_sample_transaction(doc_id, i)
                
                # トランザクションをDynamoDBに挿入
                response = transaction_table.put_item(Item=transaction_data)
                
                print(f"✅ ドキュメントID {doc_id} のトランザクション挿入成功！")
                print(f"   トランザクションID: {transaction_data['transaction_id']}")
                print(f"   金額: ¥{transaction_data['amount']}")
                successful_inserts += 1
                
            except Exception as e:
                print(f"❌ ドキュメントID {doc_id} のトランザクション挿入失敗: {e}")
        
        print(f"\n🎯 挿入結果: {successful_inserts}/{len(document_ids)} 件成功")
        
        if successful_inserts > 0:
            print("\n📊 挿入されたトランザクションを確認中...")
            
            # 挿入されたトランザクションを検索して確認
            for doc_id in document_ids[:3]:  # 最初の3件だけ確認
                try:
                    response = transaction_table.scan(
                        FilterExpression=boto3.dynamodb.conditions.Attr('document_id').eq(doc_id),
                        Limit=1
                    )
                    
                    items = response.get('Items', [])
                    if items:
                        item = items[0]
                        print(f"✅ {doc_id}: ¥{item.get('amount', 0)} - {item.get('description', 'N/A')}")
                    else:
                        print(f"❌ {doc_id}: トランザクションが見つからない")
                        
                except Exception as e:
                    print(f"❌ {doc_id} の確認でエラー: {e}")
        
    except Exception as e:
        print(f"❌ エラーが発生しましたわ: {e}")
        import traceback
        traceback.print_exc()

def create_sample_transaction(document_id: str, index: int) -> dict:
    """サンプルトランザクションデータを作成"""
    
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
    
    current_time = datetime.utcnow()
    
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
