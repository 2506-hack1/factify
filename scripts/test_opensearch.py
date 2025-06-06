#!/usr/bin/env python3
"""
OpenSearch検索機能のテストスクリプト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.opensearch_service import opensearch_service

def test_opensearch():
    print("=== OpenSearch 検索テスト開始 ===")
    
    # 1. ヘルスチェック
    print("\n1. OpenSearchクラスター接続テスト:")
    if opensearch_service.health_check():
        print("✅ 接続成功")
    else:
        print("❌ 接続失敗")
        return
    
    # 2. インデックス作成
    print("\n2. インデックス作成:")
    result = opensearch_service.create_index()
    if "error" not in result:
        print("✅ インデックス作成成功")
    else:
        print(f"⚠️  インデックス作成結果: {result}")
    
    # 3. テストドキュメント登録
    print("\n3. テストドキュメント登録:")
    test_docs = [
        {
            "id": "doc1",
            "title": "Python入門ガイド",
            "content": "Pythonは初心者にも優しいプログラミング言語です。データ分析、Web開発、AI開発など様々な用途に使用できます。",
            "user_id": "test_user"
        },
        {
            "id": "doc2", 
            "title": "AWS OpenSearch使い方",
            "content": "AWS OpenSearchは検索とログ分析に特化したマネージドサービスです。ElasticsearchとKibanaの機能を提供します。",
            "user_id": "test_user"
        },
        {
            "id": "doc3",
            "title": "機械学習の基礎",
            "content": "機械学習では大量のデータからパターンを見つけて予測モデルを構築します。教師あり学習、教師なし学習、強化学習の3つの手法があります。",
            "user_id": "test_user"
        }
    ]
    
    for doc in test_docs:
        result = opensearch_service.index_document(
            doc["id"], doc["title"], doc["content"], doc["user_id"]
        )
        if "error" not in result:
            print(f"✅ {doc['title']} 登録成功")
        else:
            print(f"❌ {doc['title']} 登録失敗: {result}")
    
    # インデックス更新待ち
    import time
    print("\n⏱️  インデックス更新待ち（3秒）...")
    time.sleep(3)
    
    # 4. 検索テスト
    print("\n4. 検索テスト:")
    test_queries = [
        "Python",
        "AWS OpenSearch", 
        "機械学習",
        "データ分析",
        "存在しないキーワード"
    ]
    
    for query in test_queries:
        print(f"\n🔍 検索: '{query}'")
        result = opensearch_service.search_documents(query, user_id="test_user")
        
        if "error" in result:
            print(f"❌ エラー: {result['error']}")
            continue
            
        hits = result.get("hits", {}).get("hits", [])
        print(f"📊 結果数: {len(hits)}")
        
        for i, hit in enumerate(hits[:2]):  # 上位2件のみ表示
            source = hit.get("_source", {})
            score = hit.get("_score", 0)
            print(f"  {i+1}. [{score:.2f}] {source.get('title', 'No Title')}")
            
            # ハイライト表示
            highlight = hit.get("highlight", {})
            if "content" in highlight:
                print(f"     💡 {highlight['content'][0][:100]}...")
    
    # 5. 全文検索テスト
    print("\n5. 全文検索テスト:")
    all_result = opensearch_service.search_documents("*", user_id="test_user", size=20)
    if "error" not in all_result:
        total_hits = all_result.get("hits", {}).get("total", {}).get("value", 0)
        print(f"✅ 全ドキュメント数: {total_hits}")
    else:
        print(f"❌ 全検索エラー: {all_result['error']}")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    test_opensearch()
