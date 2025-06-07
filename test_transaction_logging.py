#!/usr/bin/env python3
"""
トランザクション記録システムのテスト
- アクセスログテーブルの確認
- ダミーアクセスログの生成 
- トランザクション記録の動作確認
"""
import os
import sys
import boto3
from datetime import datetime

# 親ディレクトリをパスに追加（api配下のモジュールをインポートするため）
sys.path.append('/home/yotu/github/2506-hack1/factify/api')

from src.services.access_logger_service import access_logger_service


def test_access_logs_table():
    """アクセスログテーブルの接続確認"""
    print("=== アクセスログテーブル接続確認 ===")
    
    if access_logger_service.access_logs_table:
        print("✅ アクセスログテーブル接続成功")
        print(f"   テーブル名: {access_logger_service.access_logs_table_name}")
        
        # テーブル情報を取得
        try:
            table_info = access_logger_service.access_logs_table.table_status
            print(f"   テーブル状態: {table_info}")
        except Exception as e:
            print(f"   テーブル情報取得エラー: {e}")
    else:
        print("❌ アクセスログテーブル接続失敗")
        return False
    
    if access_logger_service.incentive_summary_table:
        print("✅ インセンティブ集計テーブル接続成功")
        print(f"   テーブル名: {access_logger_service.incentive_summary_table_name}")
    else:
        print("❌ インセンティブ集計テーブル接続失敗")
    
    return True


def test_dummy_access_logs():
    """ダミーアクセスログ生成テスト"""
    print("\n=== ダミーアクセスログ生成テスト ===")
    
    try:
        # 過去3日分、1日あたり3件のダミーログを生成
        success = access_logger_service.generate_dummy_access_logs(num_days=3, logs_per_day=3)
        
        if success:
            print("✅ ダミーアクセスログ生成成功！")
        else:
            print("❌ ダミーアクセスログ生成失敗")
            return False
            
    except Exception as e:
        print(f"❌ ダミーアクセスログ生成エラー: {e}")
        return False
    
    return True


def test_search_access_logging():
    """検索アクセス記録のテスト"""
    print("\n=== 検索アクセス記録テスト ===")
    
    # 実在のドキュメントIDを使用してアクセス記録をテスト
    dummy_documents = [
        {
            'id': '5f029e5c-cb8b-4f2e-9120-2b7cf718fac5',
            'user_id': 'e7140a18-e051-702b-0341-77c46b86e717',
            'title': 'Python入門ガイド',
            'file_name': 'python_guide.md'
        },
        {
            'id': 'a4b69f0e-5361-4568-9c18-cfb30ac649a2',
            'user_id': 'e7140a18-e051-702b-0341-77c46b86e717',
            'title': '機械学習の基礎',
            'file_name': 'ml_basics.md'
        }
    ]
    
    accessing_user_id = "test_searcher_user_123"
    search_query = "Python 機械学習 テスト"
    
    try:
        # アクセス記録を実行
        success = access_logger_service.log_search_access(
            accessed_documents=dummy_documents,
            accessing_user_id=accessing_user_id,
            search_query=search_query
        )
        
        if success:
            print("✅ 検索アクセス記録成功！")
            print(f"   記録ドキュメント数: {len(dummy_documents)}件")
            print(f"   検索ユーザー: {accessing_user_id}")
            print(f"   検索クエリ: {search_query}")
        else:
            print("❌ 検索アクセス記録失敗")
            return False
            
    except Exception as e:
        print(f"❌ 検索アクセス記録エラー: {e}")
        return False
    
    return True


def test_user_access_logs():
    """ユーザーアクセス履歴取得テスト"""
    print("\n=== ユーザーアクセス履歴取得テスト ===")
    
    test_user_id = "test_searcher_user_123"
    
    try:
        access_logs = access_logger_service.get_user_access_logs(user_id=test_user_id, limit=10)
        
        print(f"📋 ユーザー {test_user_id} のアクセス履歴: {len(access_logs)}件")
        
        if access_logs:
            print("   最新のアクセス履歴:")
            for i, log in enumerate(access_logs[:3]):  # 最新3件のみ表示
                print(f"   {i+1}. {log.get('accessed_document_id', 'N/A')[:8]}... - {log.get('search_query', 'N/A')}")
        else:
            print("   アクセス履歴が見つかりませんでした")
            
    except Exception as e:
        print(f"❌ ユーザーアクセス履歴取得エラー: {e}")
        return False
    
    return True


def test_incentive_calculation():
    """インセンティブ計算テスト"""
    print("\n=== インセンティブ計算テスト ===")
    
    owner_user_id = "e7140a18-e051-702b-0341-77c46b86e717"
    current_period = datetime.now().strftime('%Y-%m')
    
    try:
        incentive_data = access_logger_service.calculate_incentive_points(
            owner_user_id=owner_user_id,
            period_month=current_period
        )
        
        if incentive_data:
            print("✅ インセンティブ計算成功！")
            print(f"   所有者: {owner_user_id[:8]}...")
            print(f"   期間: {current_period}")
            print(f"   総アクセス数: {incentive_data.get('total_access_count', 0)}回")
            print(f"   ユニークユーザー数: {incentive_data.get('unique_users_count', 0)}人")
            print(f"   獲得ポイント: {incentive_data.get('total_incentive_points', 0)}pt")
        else:
            print("❌ インセンティブ計算結果が空です")
            return False
            
    except Exception as e:
        print(f"❌ インセンティブ計算エラー: {e}")
        return False
    
    return True


def main():
    print("🎯 トランザクション記録システムテスト開始ですわ～！")
    print(f"AWS_REGION: {os.environ.get('AWS_REGION', 'ap-northeast-1')}")
    
    all_success = True
    
    # 1. アクセスログテーブル接続確認
    if not test_access_logs_table():
        all_success = False
    
    # 2. ダミーアクセスログ生成
    if not test_dummy_access_logs():
        all_success = False
    
    # 3. 検索アクセス記録テスト
    if not test_search_access_logging():
        all_success = False
    
    # 4. ユーザーアクセス履歴取得テスト
    if not test_user_access_logs():
        all_success = False
    
    # 5. インセンティブ計算テスト
    if not test_incentive_calculation():
        all_success = False
    
    print(f"\n{'=' * 50}")
    if all_success:
        print("🎉 全てのテストが成功しましたわ～！")
        print("   トランザクション記録システムは正常に動作していますことよ！")
    else:
        print("⚠️  一部のテストが失敗しました")
        print("   詳細は上記のログをご確認くださいませ")
    
    print("\nNEXT ACTION:")
    print("1. WebアプリからAPI Gateway経由で検索を実行")
    print("2. Analyticsページでトランザクション記録を確認")
    print("3. 実際のユーザーがアクセスした際の記録を検証")


if __name__ == "__main__":
    main()
