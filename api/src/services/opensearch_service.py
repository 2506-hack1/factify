"""
OpenSearch最小構成検索サービス
シンプルで高性能な検索機能を提供
"""
import requests
import json
from typing import Dict, List, Optional
from ..config import OPENSEARCH_ENDPOINT


class MinimalOpenSearchService:
    """最小構成OpenSearch検索サービス"""
    
    def __init__(self):
        # HTTPエンドポイント（認証なし・デモ用）
        self.endpoint = OPENSEARCH_ENDPOINT
        self.index_name = "factify-docs"
        
    def create_index(self) -> Dict:
        """超シンプルなインデックス作成"""
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "japanese_text": {
                            "type": "cjk"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "japanese_text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "text", 
                        "analyzer": "japanese_text"
                    },
                    "user_id": {"type": "keyword"},
                    "file_type": {"type": "keyword"},
                    "uploaded_at": {"type": "date"}
                }
            }
        }
        
        try:
            response = requests.put(
                f"{self.endpoint}/{self.index_name}",
                json=mapping,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"インデックス作成結果: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"インデックス作成エラー: {e}")
            return {"error": str(e)}

    def index_document(self, doc_id: str, title: str, content: str, 
                      user_id: str, file_type: str = "unknown", uploaded_at: str = None) -> Dict:
        """ドキュメント登録"""
        from datetime import datetime
        
        doc = {
            "title": title,
            "content": content,
            "user_id": user_id,
            "file_type": file_type,
            "uploaded_at": uploaded_at or datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.put(
                f"{self.endpoint}/{self.index_name}/_doc/{doc_id}",
                json=doc,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"ドキュメント登録: {doc_id} -> {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"ドキュメント登録エラー: {e}")
            return {"error": str(e)}

    def search(self, query: str, user_id: str = None, size: int = 10) -> Dict:
        """シンプル検索"""
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content"],  # タイトル重要視
                                "fuzziness": "AUTO",  # typo許容
                                "operator": "or"
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150, "number_of_fragments": 2}
                }
            },
            "size": size
        }
        
        # ユーザーフィルター追加
        if user_id:
            search_body["query"]["bool"]["filter"] = [
                {"term": {"user_id": user_id}}
            ]
        
        try:
            response = requests.post(
                f"{self.endpoint}/{self.index_name}/_search",
                json=search_body,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"検索実行: '{query}' -> {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"検索エラー: {e}")
            return {"error": str(e)}

    def delete_document(self, doc_id: str) -> Dict:
        """ドキュメント削除"""
        try:
            response = requests.delete(
                f"{self.endpoint}/{self.index_name}/_doc/{doc_id}",
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"ドキュメント削除エラー: {e}")
            return {"error": str(e)}

    def health_check(self) -> bool:
        """ヘルスチェック"""
        try:
            response = requests.get(f"{self.endpoint}/_cluster/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# シングルトンインスタンス
opensearch_service = MinimalOpenSearchService()
