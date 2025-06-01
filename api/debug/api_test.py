#!/usr/bin/env python3
"""
APIエンドポイントをテストするためのデバッグスクリプト
"""
import requests
import argparse
import json
import os
import sys
from pprint import pprint

# デフォルトのAPI URLを設定
DEFAULT_API_URL = "http://localhost:8000"

def test_upload_file(api_url, file_path, title, description=None):
    """ファイルアップロードエンドポイントをテストする"""
    if not os.path.exists(file_path):
        print(f"エラー: ファイル {file_path} が見つかりません。")
        return
    
    # アップロードするファイルを準備
    file_name = os.path.basename(file_path)
    files = {'file': (file_name, open(file_path, 'rb'), 'text/plain')}
    
    # フォームデータを準備
    data = {'title': title}
    if description:
        data['description'] = description
    
    try:
        # POSTリクエストを送信
        response = requests.post(f"{api_url}/upload/", files=files, data=data)
        
        # レスポンスを表示
        print(f"ステータスコード: {response.status_code}")
        if response.status_code == 200:
            print("アップロード成功:")
            pprint(response.json())
        else:
            print("アップロード失敗:")
            print(response.text)
    
    except Exception as e:
        print(f"エラー: リクエスト中にエラーが発生しました: {str(e)}")

def test_list_files(api_url):
    """ファイル一覧取得エンドポイントをテストする"""
    try:
        response = requests.get(f"{api_url}/files/")
        
        print(f"ステータスコード: {response.status_code}")
        if response.status_code == 200:
            files = response.json()
            if not files:
                print("ファイルはまだアップロードされていません。")
            else:
                print(f"合計 {len(files)} 件のファイルが見つかりました:")
                for i, file in enumerate(files, 1):
                    print(f"\n{i}. ID: {file['id']}")
                    print(f"   タイトル: {file['title']}")
                    print(f"   ファイル名: {file['file_name']}")
                    print(f"   アップロード日時: {file['uploaded_at']}")
        else:
            print("ファイル一覧の取得に失敗しました:")
            print(response.text)
    
    except Exception as e:
        print(f"エラー: リクエスト中にエラーが発生しました: {str(e)}")

def test_get_file(api_url, file_id):
    """特定のファイル取得エンドポイントをテストする"""
    try:
        response = requests.get(f"{api_url}/files/{file_id}")
        
        print(f"ステータスコード: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            print("\nファイルのメタデータ:")
            metadata = data["metadata"]
            print(f"ID: {metadata['id']}")
            print(f"タイトル: {metadata['title']}")
            print(f"説明: {metadata.get('description', '')}")
            print(f"ファイル名: {metadata['file_name']}")
            print(f"アップロード日時: {metadata['uploaded_at']}")
            
            # ファイル内容（先頭500文字のみ表示）
            content = data["content"]
            print("\nファイルの内容（先頭500文字）:")
            print("-" * 50)
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
            print("-" * 50)
            
            # 正規化されたテキスト（先頭500文字のみ表示）
            cleaned_content = data["cleaned_content"]
            print("\n正規化されたテキスト（先頭500文字）:")
            print("-" * 50)
            if len(cleaned_content) > 500:
                print(cleaned_content[:500] + "...")
            else:
                print(cleaned_content)
            print("-" * 50)
        else:
            print(f"ファイル (ID: {file_id}) の取得に失敗しました:")
            print(response.text)
    
    except Exception as e:
        print(f"エラー: リクエスト中にエラーが発生しました: {str(e)}")

def test_delete_file(api_url, file_id):
    """ファイル削除エンドポイントをテストする"""
    try:
        response = requests.delete(f"{api_url}/files/{file_id}")
        
        print(f"ステータスコード: {response.status_code}")
        if response.status_code == 200:
            print("ファイルの削除に成功しました:")
            pprint(response.json())
        else:
            print(f"ファイル (ID: {file_id}) の削除に失敗しました:")
            print(response.text)
    
    except Exception as e:
        print(f"エラー: リクエスト中にエラーが発生しました: {str(e)}")

def test_api_availability(api_url):
    """APIサーバーが利用可能かテストする"""
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            print(f"✅ APIサーバーは利用可能です (URL: {api_url})")
            return True
        else:
            print(f"❌ APIサーバーは応答しましたが、ステータスコードが異常です: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"❌ APIサーバーに接続できません (URL: {api_url})")
        print("  サーバーが起動しているか確認してください。")
        return False
    except Exception as e:
        print(f"❌ APIサーバーの確認中にエラーが発生しました: {str(e)}")
        return False

def create_sample_text_file(file_path, content=None):
    """サンプルのテキストファイルを作成する"""
    if content is None:
        content = """これはサンプルのテキストファイルです。
        
APIテスト用のテキストファイルとして作成されました。

このファイルはAPIを通じてS3にアップロードされ、
そのメタデータはDynamoDBに保存されます。

テキストの正規化機能のテストにも使用できます。
複数行のテキスト
タブ文字や　全角スペースなども含まれています。
"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"サンプルファイルが作成されました: {file_path}")
        return True
    except Exception as e:
        print(f"サンプルファイルの作成中にエラーが発生しました: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='FastAPI エンドポイントをテストするためのデバッグスクリプト')
    
    # 共通オプション
    parser.add_argument('--url', '-u', default=DEFAULT_API_URL,
                        help=f'APIのベースURL (デフォルト: {DEFAULT_API_URL})')
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest='command', help='実行するコマンド')
    
    # check コマンド
    check_parser = subparsers.add_parser('check', help='APIサーバーの状態を確認する')
    
    # upload コマンド
    upload_parser = subparsers.add_parser('upload', help='ファイルをアップロードする')
    upload_parser.add_argument('file_path', help='アップロードするファイルのパス')
    upload_parser.add_argument('--title', '-t', required=True, help='ファイルのタイトル')
    upload_parser.add_argument('--description', '-d', help='ファイルの説明')
    
    # list コマンド
    list_parser = subparsers.add_parser('list', help='アップロードされたファイルの一覧を表示する')
    
    # get コマンド
    get_parser = subparsers.add_parser('get', help='特定のファイルの詳細を表示する')
    get_parser.add_argument('file_id', help='取得するファイルのID')
    
    # delete コマンド
    delete_parser = subparsers.add_parser('delete', help='ファイルを削除する')
    delete_parser.add_argument('file_id', help='削除するファイルのID')
    
    # sample コマンド
    sample_parser = subparsers.add_parser('sample', help='サンプルのテキストファイルを作成する')
    sample_parser.add_argument('--output', '-o', default='api_sample.txt', help='作成するファイルのパス (デフォルト: api_sample.txt)')
    
    # 引数のパース
    args = parser.parse_args()
    
    # コマンドがない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return
    
    # API利用可能性の確認（check以外のAPIコマンドの前に実行）
    if args.command not in ['check', 'sample'] and not test_api_availability(args.url):
        print("APIサーバーが利用できません。サーバーが起動しているか確認してください。")
        return
    
    # コマンドに応じた処理
    if args.command == 'check':
        test_api_availability(args.url)
    elif args.command == 'upload':
        test_upload_file(args.url, args.file_path, args.title, args.description)
    elif args.command == 'list':
        test_list_files(args.url)
    elif args.command == 'get':
        test_get_file(args.url, args.file_id)
    elif args.command == 'delete':
        test_delete_file(args.url, args.file_id)
    elif args.command == 'sample':
        create_sample_text_file(args.output)

if __name__ == "__main__":
    main()
