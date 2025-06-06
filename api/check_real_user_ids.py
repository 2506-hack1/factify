#!/usr/bin/env python3
"""
実際のユーザーIDとドキュメントIDを確認するスクリプト
"""
import os
import boto3
import json

def main():
    try:
        print("🔍 実際のユーザーIDとドキュメントを確認いたしますわ～！")
        
        # DynamoDBクライアント初期化
        dynamodb = boto3.resource('dynamodb')
        table_name = "factify-dynamodb-table-471112951833-ap-northeast-1"
        
        table = dynamodb.Table(table_name)
        
        # ドキュメントタイプのアイテムをスキャン
        print("📄 ドキュメント一覧を取得中...")
        
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('type').eq('document'),
            ProjectionExpression='id, title, owner_user_id, created_at'
        )
        
        documents = response.get('Items', [])
        
        if not documents:
            print("❌ ドキュメントが見つかりませんでした")
            
            # 全てのアイテムを確認
            print("\n🔍 全アイテムを確認中...")
            all_response = table.scan(
                ProjectionExpression='id, #type, title, owner_user_id',
                ExpressionAttributeNames={'#type': 'type'},
                Limit=10
            )
            
            for item in all_response.get('Items', []):
                print(f"  ID: {item.get('id', 'N/A')}")
                print(f"  Type: {item.get('type', 'N/A')}")
                print(f"  Title: {item.get('title', 'N/A')}")
                print(f"  Owner: {item.get('owner_user_id', 'N/A')}")
                print("  ---")
            return
        
        print(f"✅ {len(documents)}件のドキュメントが見つかりました！")
        
        # ユーザーIDをグループ化
        user_docs = {}
        
        for doc in documents:
            owner_id = doc.get('owner_user_id', 'unknown')
            if owner_id not in user_docs:
                user_docs[owner_id] = []
            user_docs[owner_id].append(doc)
        
        print(f"\n👥 ユーザー別ドキュメント数:")
        for user_id, docs in user_docs.items():
            print(f"  {user_id}: {len(docs)}件")
            
            # 最初の3件のドキュメントIDを表示
            for i, doc in enumerate(docs[:3]):
                print(f"    📄 {doc.get('id', 'N/A')} - {doc.get('title', 'No title')}")
        
        # 最初のユーザーの情報を詳細表示
        if user_docs:
            first_user = list(user_docs.keys())[0]
            first_user_docs = user_docs[first_user]
            
            print(f"\n🎯 実際のユーザーID: {first_user}")
            print(f"📄 そのユーザーのドキュメントID一覧:")
            
            doc_ids = []
            for doc in first_user_docs[:5]:  # 最初の5件
                doc_id = doc.get('id')
                doc_ids.append(doc_id)
                print(f"  - {doc_id}")
            
            print(f"\n💡 このユーザーID ({first_user}) を使ってトランザクション/インセンティブデータを作成する必要がありますわ！")
            
            # Python配列形式で出力
            print(f"\n📝 更新用ドキュメントID配列:")
            print("document_ids = [")
            for doc_id in doc_ids:
                print(f"    '{doc_id}',")
            print("]")
            
            print(f"\nreal_user_id = '{first_user}'")
        
    except Exception as e:
        print(f"❌ エラーが発生しましたわ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
