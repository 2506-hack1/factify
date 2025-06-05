"""
OpenSearch最小構成検索サービス
AWS OpenSearchサービス対応版（認証付き）
"""
import requests
import json
from typing import Dict, List, Optional
from requests.auth import HTTPBasicAuth
from ..config import OPENSEARCH_ENDPOINT, OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD


class MinimalOpenSearchService:
    """AWS OpenSearch検索サービス（認証対応版）"""
    
    def __init__(self):
        # HTTPS エンドポイント（認証付き）
        self.endpoint = OPENSEARCH_ENDPOINT
        self.index_name = "factify-docs"
        self.auth = HTTPBasicAuth(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD)
        # SSL証明書の検証を有効化
        self.verify_ssl = True
        
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
                auth=self.auth,
                verify=self.verify_ssl,
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
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=10
            )
            print(f"ドキュメント登録: {doc_id} -> {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"ドキュメント登録エラー: {e}")
            return {"error": str(e)}

    def search_documents(self, query: str, user_id: str = None, size: int = 10) -> Dict:
        """シンプル検索"""
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        # 完全一致（高スコア）
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^5", "content^2"],
                                "type": "phrase",
                                "boost": 3.0
                            }
                        },
                        # 部分一致（中スコア）
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content"],
                                "operator": "and",
                                "minimum_should_match": "75%"
                            }
                        },
                        # 単語レベル一致（低スコア）
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^2", "content"],
                                "operator": "or",
                                "minimum_should_match": "50%",
                                "boost": 0.5
                            }
                        },
                        # typo許容（最低スコア）
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title", "content"],
                                "fuzziness": "1",  # 1文字までのtypo許容
                                "operator": "and",
                                "boost": 0.2
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150, "number_of_fragments": 2}
                }
            },
            "min_score": 0.2,  # 最小スコア閾値（typo許容のため少し下げる）
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
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=10
            )
            print(f"検索実行: '{query}' -> {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"検索エラー: {e}")
            return {"error": str(e)}

    def search(self, query: str, user_id: str = None, size: int = 10) -> Dict:
        """search_documentsのエイリアス（互換性のため）"""
        return self.search_documents(query, user_id, size)

    def delete_document(self, doc_id: str) -> Dict:
        """ドキュメント削除"""
        try:
            response = requests.delete(
                f"{self.endpoint}/{self.index_name}/_doc/{doc_id}",
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"ドキュメント削除エラー: {e}")
            return {"error": str(e)}

    def health_check(self) -> bool:
        """ヘルスチェック"""
        try:
            response = requests.get(
                f"{self.endpoint}/_cluster/health", 
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# シングルトンインスタンス
opensearch_service = MinimalOpenSearchService()
