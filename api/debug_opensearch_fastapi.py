#!/usr/bin/env python3
"""
OpenSearch + FastAPI統合デバッグスクリプト
認証無しでテストして問題を特定
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.opensearch_service import opensearch_service

def debug_opensearch_issue():
    print("=== OpenSearch + FastAPI 統合デバッグ ===")
    
    # 1. OpenSearchヘルスチェック
    print("\n1. OpenSearchヘルスチェック:")
    if opensearch_service.health_check():
        print("✅ OpenSearch接続OK")
    else:
        print("❌ OpenSearch接続NG")
        return
    
    # 2. 全ドキュメント確認（フィルター無し）
    print("\n2. 全ドキュメント検索（user_idフィルター無し）:")
    result_all = opensearch_service.search_documents("Python", user_id=None, size=10)
    if "error" not in result_all:
        hits_all = result_all.get("hits", {}).get("hits", [])
        print(f"✅ フィルター無し結果: {len(hits_all)}件")
        for hit in hits_all:
            source = hit["_source"]
            print(f"  - ID: {hit['_id']}, user_id: {source.get('user_id')}, title: {source.get('title')}")
    else:
        print(f"❌ エラー: {result_all['error']}")
    
    # 3. test_userでフィルター
    print("\n3. test_userでフィルター検索:")
    result_test_user = opensearch_service.search_documents("Python", user_id="test_user", size=10)
    if "error" not in result_test_user:
        hits_test = result_test_user.get("hits", {}).get("hits", [])
        print(f"✅ test_userフィルター結果: {len(hits_test)}件")
    else:
        print(f"❌ エラー: {result_test_user['error']}")
    
    # 4. 実際のユーザーIDでフィルター
    print("\n4. 実際のユーザーID（e7140a18-e051-702b-0341-77c46b86e717）でフィルター:")
    result_real_user = opensearch_service.search_documents("AWS", user_id="e7140a18-e051-702b-0341-77c46b86e717", size=10)
    if "error" not in result_real_user:
        hits_real = result_real_user.get("hits", {}).get("hits", [])
        print(f"✅ 実ユーザーフィルター結果: {len(hits_real)}件")
    else:
        print(f"❌ エラー: {result_real_user['error']}")
    
    # 5. FastAPIが使用する可能性のあるユーザーID形式を確認
    print("\n5. OpenSearchに存在する全ユーザーID一覧:")
    all_docs = opensearch_service.search_documents("*", user_id=None, size=20)
    if "error" not in all_docs:
        user_ids = set()
        for hit in all_docs.get("hits", {}).get("hits", []):
            user_id = hit["_source"].get("user_id")
            if user_id:
                user_ids.add(user_id)
        print("存在するユーザーID:")
        for uid in sorted(user_ids):
            print(f"  - {uid}")
    
    print("\n=== デバッグ完了 ===")

if __name__ == "__main__":
    debug_opensearch_issue()
