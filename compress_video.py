#!/usr/bin/env python3
"""
Discord動画圧縮ツール (Python版)
使用法: python compress_video.py <入力ファイル> [出力ファイル]
500MB以下に動画を圧縮します
"""

import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path
import json
import re

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class VideoCompressor:
    def __init__(self):
        self.check_ffmpeg()
    
    def check_ffmpeg(self):
        """ffmpegの存在確認"""
        if not shutil.which('ffmpeg'):
            print(f"{Colors.RED}エラー: ffmpegがインストールされていません{Colors.NC}")
            print("以下のコマンドでインストールしてください:")
            print("  macOS: brew install ffmpeg")
            print("  Ubuntu: sudo apt install ffmpeg")
            print("  Windows: https://ffmpeg.org/download.html")
            sys.exit(1)
    
    def get_file_size_mb(self, file_path):
        """ファイルサイズを取得（MB単位）"""
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def get_video_info(self, file_path):
        """動画の情報を取得"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(file_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}エラー: 動画情報の取得に失敗しました{Colors.NC}")
            print(f"ffprobe error: {e.stderr}")
            sys.exit(1)
    
    def get_video_duration(self, video_info):
        """動画の長さを取得（秒）"""
        return float(video_info['format']['duration'])
    
    def calculate_target_bitrate(self, target_size_mb, duration_sec):
        """目標ビットレートを計算"""
        target_size_bits = target_size_mb * 8 * 1024 * 1024
        target_bitrate = int(target_size_bits / duration_sec)
        
        # 音声ビットレート（128kbps）を差し引く
        audio_bitrate = 128000
        video_bitrate = target_bitrate - audio_bitrate
        
        # 最小ビットレートを確保
        if video_bitrate < 500000:
            video_bitrate = 500000
            
        return video_bitrate
    
    def run_ffmpeg_with_progress(self, cmd, duration, pass_name):
        """ffmpegを実行してプログレスを表示"""
        print(f"{Colors.YELLOW}{pass_name}...{Colors.NC}")
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True
        )
        
        # プログレス監視
        for line in process.stderr:
            # 時間の進行を取得
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                
                if duration > 0:
                    progress = min(current_time / duration * 100, 100)
                    print(f"\r進行状況: {progress:.1f}%", end='', flush=True)
        
        process.wait()
        print()  # 改行
        
        if process.returncode != 0:
            error_output = process.stderr.read() if process.stderr else "Unknown error"
            print(f"{Colors.RED}エラー: ffmpegの実行に失敗しました{Colors.NC}")
            print(f"Error details: {error_output}")
            sys.exit(1)
    
    def compress_video(self, input_file, output_file, target_size_mb=45):
        """動画を圧縮"""
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # 入力ファイルの確認
        if not input_path.exists():
            print(f"{Colors.RED}エラー: ファイル '{input_file}' が見つかりません{Colors.NC}")
            sys.exit(1)
        
        # 現在のファイルサイズを確認
        current_size_mb = self.get_file_size_mb(input_path)
        print(f"{Colors.BLUE}入力ファイル:{Colors.NC} {input_file}")
        print(f"{Colors.BLUE}現在のサイズ:{Colors.NC} {current_size_mb:.2f}MB")
        print(f"{Colors.BLUE}目標サイズ:{Colors.NC} {target_size_mb}MB")
        
        # 既に目標サイズ以下の場合
        if current_size_mb <= target_size_mb:
            print(f"{Colors.GREEN}ファイルは既に目標サイズ以下です。コピーのみ実行します。{Colors.NC}")
            shutil.copy2(input_path, output_path)
            print(f"{Colors.GREEN}完了: {output_file}{Colors.NC}")
            return
        
        # 動画情報を取得
        video_info = self.get_video_info(input_path)
        duration = self.get_video_duration(video_info)
        print(f"{Colors.BLUE}動画の長さ:{Colors.NC} {duration:.2f}秒")
        
        # 目標ビットレートを計算
        target_bitrate = self.calculate_target_bitrate(target_size_mb, duration)
        print(f"{Colors.BLUE}目標ビットレート:{Colors.NC} {target_bitrate}bps")
        
        print(f"{Colors.YELLOW}圧縮を開始しています...{Colors.NC}")
        
        # 2-pass エンコーディング
        # Pass 1
        cmd_pass1 = [
            'ffmpeg', '-y', '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', str(target_bitrate),
            '-pass', '1',
            '-preset', 'medium',
            '-f', 'null',
            '/dev/null' if os.name != 'nt' else 'NUL'
        ]
        
        self.run_ffmpeg_with_progress(cmd_pass1, duration, "Pass 1/2: 分析中")
        
        # Pass 2
        cmd_pass2 = [
            'ffmpeg', '-y', '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', str(target_bitrate),
            '-pass', '2',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            str(output_path)
        ]
        
        self.run_ffmpeg_with_progress(cmd_pass2, duration, "Pass 2/2: エンコード中")
        
        # ログファイルを削除
        for log_file in ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']:
            if os.path.exists(log_file):
                os.remove(log_file)
        
        # 結果を表示
        output_size_mb = self.get_file_size_mb(output_path)
        compression_ratio = 100 - (output_size_mb * 100 / current_size_mb)
        
        print()
        print(f"{Colors.GREEN}圧縮完了!{Colors.NC}")
        print(f"{Colors.BLUE}出力ファイル:{Colors.NC} {output_file}")
        print(f"{Colors.BLUE}圧縮後サイズ:{Colors.NC} {output_size_mb:.2f}MB")
        print(f"{Colors.BLUE}圧縮率:{Colors.NC} {compression_ratio:.1f}%")
        
        # Discord制限チェック
        if output_size_mb <= 50:
            print(f"{Colors.GREEN}✅ Discordにアップロード可能です{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}⚠️  まだ50MBを超えています。さらに圧縮が必要です{Colors.NC}")

def main():
    parser = argparse.ArgumentParser(
        description="Discord用動画圧縮ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python compress_video.py input.mov
  python compress_video.py input.mov output.mp4
  python compress_video.py input.mov -s 300
        """
    )
    
    parser.add_argument('input_file', help='入力動画ファイル')
    parser.add_argument('output_file', nargs='?', help='出力ファイル名（省略時は自動生成）')
    parser.add_argument('-s', '--size', type=int, default=45, 
                       help='目標サイズをMBで指定（デフォルト: 45MB）')
    
    args = parser.parse_args()
    
    # 出力ファイル名の生成
    if not args.output_file:
        input_path = Path(args.input_file)
        stem = input_path.stem
        args.output_file = f"{stem}_compressed.mp4"
    
    # 圧縮実行
    compressor = VideoCompressor()
    compressor.compress_video(args.input_file, args.output_file, args.size)

if __name__ == '__main__':
    main()