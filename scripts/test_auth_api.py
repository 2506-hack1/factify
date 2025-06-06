#!/usr/bin/env python3
"""
認証付きSearch APIテストスクリプト
"""
import requests
import json
import argparse
from pprint import pprint

# デフォルトのAPI URL
DEFAULT_API_URL = "http://localhost:8001"

class AuthenticatedAPITester:
    def __init__(self, api_url, access_token):
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def test_search_api(self, query, language="ja", max_results=10, user_only=True):
        """Search APIをテストする"""
        print(f"🔍 Search APIテスト開始...")
        print(f"検索クエリ: {query}")
        print(f"言語: {language}")
        print(f"最大結果数: {max_results}")
        print(f"ユーザー固有検索: {user_only}")
        print("-" * 50)
        
        # リクエストボディ
        payload = {
            "query": query,
            "language": language,
            "max_results": max_results,
            "user_only": user_only
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/search",
                headers=self.headers,
                json=payload
            )
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Search API成功:")
                result = response.json()
                print(f"検索クエリ: {result['query']}")
                print(f"総結果数: {result['total_results']}")
                print(f"成功: {result['success']}")
                
                if result['results']:
                    print("\n📄 検索結果:")
                    for i, doc in enumerate(result['results'], 1):
                        print(f"\n{i}. ID: {doc['id']}")
                        print(f"   タイトル: {doc['title']}")
                        print(f"   ファイル名: {doc['file_name']}")
                        print(f"   ファイルタイプ: {doc['file_type']}")
                        print(f"   アップロード日時: {doc['uploaded_at']}")
                        print(f"   説明: {doc.get('description', 'なし')}")
                        # テキストの先頭100文字のみ表示
                        formatted_text = doc.get('formatted_text', '')
                        if formatted_text:
                            preview = formatted_text[:100] + "..." if len(formatted_text) > 100 else formatted_text
                            print(f"   テキストプレビュー: {preview}")
                else:
                    print("検索結果はありませんでした。")
                    
            elif response.status_code == 401:
                print("❌ 認証エラー: トークンが無効または期限切れです")
                print("レスポンス:", response.text)
            elif response.status_code == 400:
                print("❌ バリデーションエラー:")
                print("レスポンス:", response.text)
            else:
                print(f"❌ Search API失敗:")
                print("レスポンス:", response.text)
                
        except Exception as e:
            print(f"❌ エラー: {str(e)}")
    
    def test_user_files_api(self):
        """ユーザーファイル一覧APIをテストする"""
        print(f"📁 ユーザーファイル一覧APIテスト開始...")
        print("-" * 50)
        
        try:
            response = requests.get(
                f"{self.api_url}/files/user",
                headers=self.headers
            )
            
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ ユーザーファイル一覧API成功:")
                result = response.json()
                print(f"ユーザーID: {result['user_id']}")
                print(f"総ファイル数: {result['total_files']}")
                
                if result['files']:
                    print("\n📄 ファイル一覧:")
                    for i, file in enumerate(result['files'], 1):
                        print(f"\n{i}. ID: {file['id']}")
                        print(f"   タイトル: {file['title']}")
                        print(f"   ファイル名: {file['file_name']}")
                        print(f"   ファイルタイプ: {file['file_type']}")
                        print(f"   アップロード日時: {file['uploaded_at']}")
                else:
                    print("アップロードされたファイルはありません。")
                    
            elif response.status_code == 401:
                print("❌ 認証エラー: トークンが無効または期限切れです")
            else:
                print(f"❌ API失敗:")
                print("レスポンス:", response.text)
                
        except Exception as e:
            print(f"❌ エラー: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='認証付きSearch APIテストスクリプト')
    
    # 共通オプション
    parser.add_argument('--url', '-u', default=DEFAULT_API_URL,
                        help=f'APIのベースURL (デフォルト: {DEFAULT_API_URL})')
    parser.add_argument('--token', '-t', required=True,
                        help='Cognitoアクセストークン')
    
    # サブコマンド
    subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
    
    # search コマンド
    search_parser = subparsers.add_parser('search', help='Search APIをテストする')
    search_parser.add_argument('query', help='検索クエリ')
    search_parser.add_argument('--language', '-l', default='ja', help='言語 (デフォルト: ja)')
    search_parser.add_argument('--max-results', '-m', type=int, default=10, help='最大結果数 (デフォルト: 10)')
    search_parser.add_argument('--all-users', action='store_true', help='全ユーザーのファイルを検索 (デフォルト: 自分のファイルのみ)')
    
    # files コマンド
    files_parser = subparsers.add_parser('files', help='ユーザーファイル一覧を取得する')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # APIテスターの初期化
    tester = AuthenticatedAPITester(args.url, args.token)
    
    # コマンドに応じた処理
    if args.command == 'search':
        user_only = not args.all_users
        tester.test_search_api(args.query, args.language, args.max_results, user_only)
    elif args.command == 'files':
        tester.test_user_files_api()

if __name__ == "__main__":
    main()
