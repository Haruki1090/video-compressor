#!/usr/bin/env python3
"""
動画圧縮ツールテストスクリプト
各機能の動作確認用
"""

import os
import sys
import subprocess
from pathlib import Path
import tempfile
import shutil

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def run_command(cmd, description):
    """コマンドを実行してテスト"""
    print(f"{Colors.BLUE}テスト: {description}{Colors.NC}")
    print(f"コマンド: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ 成功{Colors.NC}")
            if result.stdout:
                print(f"出力: {result.stdout[:200]}...")
        else:
            print(f"{Colors.RED}❌ 失敗{Colors.NC}")
            print(f"エラー: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ 例外発生: {e}{Colors.NC}")
        return False

def create_test_video():
    """テスト用動画を作成"""
    print(f"{Colors.YELLOW}テスト用動画を作成しています...{Colors.NC}")
    
    # ffmpegでテスト動画を生成
    test_file = "test_video.mp4"
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=duration=10:size=1280x720:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=10',
        '-c:v', 'libx264', '-c:a', 'aac', '-t', '10', test_file
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"{Colors.GREEN}✅ テスト動画を作成しました: {test_file}{Colors.NC}")
        return test_file
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ テスト動画の作成に失敗しました: {e}{Colors.NC}")
        return None

def main():
    print(f"{Colors.CYAN}動画圧縮ツール テストスクリプト{Colors.NC}")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    script_path = Path("compress_video.py")
    if not script_path.exists():
        print(f"{Colors.RED}エラー: compress_video.py が見つかりません{Colors.NC}")
        sys.exit(1)
    
    test_results = []
    
    # 1. ヘルプ表示テスト
    success = run_command(
        ['python3', 'compress_video.py', '--help'],
        "ヘルプ表示"
    )
    test_results.append(("ヘルプ表示", success))
    print()
    
    # 2. プロファイル一覧表示テスト
    success = run_command(
        ['python3', 'compress_video.py', '--list-profiles'],
        "プロファイル一覧表示"
    )
    test_results.append(("プロファイル一覧", success))
    print()
    
    # 3. 設定ファイル存在確認
    config_exists = Path("config.json").exists()
    print(f"{Colors.BLUE}テスト: 設定ファイル確認{Colors.NC}")
    if config_exists:
        print(f"{Colors.GREEN}✅ config.json が存在します{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  config.json が見つかりません{Colors.NC}")
    test_results.append(("設定ファイル", config_exists))
    print()
    
    # 4. テスト動画での圧縮テスト（ffmpegが利用可能な場合のみ）
    if shutil.which('ffmpeg'):
        test_video = create_test_video()
        if test_video:
            # 基本圧縮テスト
            success = run_command(
                ['python3', 'compress_video.py', test_video, 'output_test.mp4', '-s', '5'],
                "基本圧縮テスト"
            )
            test_results.append(("基本圧縮", success))
            
            # クリーンアップ
            for file in [test_video, 'output_test.mp4']:
                if os.path.exists(file):
                    os.remove(file)
            print()
    else:
        print(f"{Colors.YELLOW}⚠️  ffmpegが見つからないため、動画圧縮テストはスキップします{Colors.NC}")
        test_results.append(("動画圧縮", False))
        print()
    
    # テスト結果サマリー
    print(f"{Colors.CYAN}テスト結果サマリー{Colors.NC}")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{Colors.GREEN}PASS{Colors.NC}" if result else f"{Colors.RED}FAIL{Colors.NC}"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print()
    print(f"合格: {passed}/{total}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 全てのテストが成功しました！{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  一部のテストが失敗しました{Colors.NC}")
    
    # 使用例を表示
    print(f"\n{Colors.BLUE}使用例:{Colors.NC}")
    print("基本的な圧縮:")
    print("  python3 compress_video.py input.mov")
    print("\nプロファイルを使用:")
    print("  python3 compress_video.py input.mov -p discord")
    print("\nバッチ処理:")
    print("  python3 compress_video.py --batch /path/to/videos")
    print("\n品質設定:")
    print("  python3 compress_video.py input.mov -q slow -s 100")

if __name__ == '__main__':
    main() 