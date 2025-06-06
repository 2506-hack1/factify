#!/usr/bin/env python3
"""
実在するドキュメントIDを調査するデバッグスクリプト
"""
import os
import sys
import boto3
from boto3.dynamodb.conditions import Attr

def main():
    try:
        print("🔍 DynamoDBドキュメント調査開始")
        print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'Not set')}")
        
        # DynamoDBクライアント初期化
        dynamodb = boto3.resource('dynamodb')
        
        # テーブル名を推定（リージョンとアカウントIDから）
        region = os.environ.get('AWS_REGION', 'ap-northeast-1')
        
        # 実際のテーブル名を使用（アカウントIDを含む）
        possible_table_names = [
            "factify-dynamodb-table-471112951833-ap-northeast-1",
            f"factify-dynamodb-table-471112951833-{region}",
            f"factify-documents-{region}",
            "factify-documents",
            "factify-dynamodb-table"
        ]
        
        table = None
        table_name = None
        
        for name in possible_table_names:
            try:
                test_table = dynamodb.Table(name)
                # テーブルの存在確認
                test_table.load()
                table = test_table
                table_name = name
                print(f"✅ テーブル発見: {name}")
                break
            except Exception as e:
                print(f"❌ テーブル {name} が見つからない: {str(e)[:50]}...")
                continue
        
        if not table:
            print("❌ ドキュメントテーブルが見つかりませんでした")
            
            # テーブル一覧を取得してみる
            print("\n📋 利用可能なテーブル一覧:")
            client = boto3.client('dynamodb')
            tables = client.list_tables()
            for table_name in tables.get('TableNames', []):
                print(f"  - {table_name}")
            return
        
        # ドキュメントをスキャン
        print(f"\n📄 テーブル '{table_name}' からドキュメントを取得中...")
        
        response = table.scan(
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression='id, title, file_name, user_id',
            Limit=20
        )
        
        items = response.get('Items', [])
        print(f"✅ 発見されたドキュメント数: {len(items)}件")
        
        if items:
            print("\n📄 実在するドキュメントID一覧:")
            for i, item in enumerate(items):
                print(f"{i+1:2d}. ID: {item.get('id', 'N/A')}")
                print(f"    タイトル: {item.get('title', 'N/A')}")
                print(f"    ファイル名: {item.get('file_name', 'N/A')}")
                print(f"    ユーザーID: {item.get('user_id', 'N/A')}")
                print()
                
            # 最初の5つのIDを抽出してダミーデータ用に保存
            real_doc_ids = [item.get('id') for item in items[:5] if item.get('id')]
            print("🎯 ダミーデータ用ドキュメントID:")
            for doc_id in real_doc_ids:
                print(f"  '{doc_id}',")
                
        else:
            print("❌ ドキュメントが見つかりませんでした")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
