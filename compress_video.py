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
import time
import threading

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

class ProgressBar:
    def __init__(self, total_duration):
        self.total_duration = total_duration
        self.current_time = 0
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.spinner_index = 0
        self.is_running = True
        
    def update_progress(self, current_time):
        self.current_time = current_time
        
    def draw_progress_bar(self, progress, width=40):
        filled = int(width * progress / 100)
        bar = "█" * filled + "▒" * (width - filled)
        return f"[{bar}]"
        
    def animate_spinner(self):
        while self.is_running:
            progress = min(self.current_time / self.total_duration * 100, 100) if self.total_duration > 0 else 0
            spinner = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]
            progress_bar = self.draw_progress_bar(progress)
            
            elapsed_mins = int(self.current_time // 60)
            elapsed_secs = int(self.current_time % 60)
            
            print(f"\r{Colors.CYAN}{spinner}{Colors.NC} {progress_bar} {progress:.1f}% "
                  f"({elapsed_mins:02d}:{elapsed_secs:02d})", end='', flush=True)
            
            self.spinner_index += 1
            time.sleep(0.1)
            
    def stop(self):
        self.is_running = False

class VideoCompressor:
    def __init__(self, config_file=None):
        self.check_ffmpeg()
        self.quality_presets = {
            'fast': {'preset': 'fast', 'crf': 28},
            'medium': {'preset': 'medium', 'crf': 23},
            'slow': {'preset': 'slow', 'crf': 20},
            'high': {'preset': 'slower', 'crf': 18}
        }
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file=None):
        """設定ファイルを読み込み"""
        if config_file is None:
            # スクリプトと同じディレクトリのconfig.jsonを探す
            script_dir = Path(__file__).parent
            config_file = script_dir / "config.json"
        
        if Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"{Colors.YELLOW}警告: 設定ファイル読み込みエラー - {e}{Colors.NC}")
        
        # デフォルト設定を返す
        return {
            "default_settings": {
                "target_size_mb": 45,
                "quality_preset": "medium",
                "audio_bitrate": "128k"
            },
            "profiles": {}
        }
    
    def get_profile_settings(self, profile_name):
        """プロファイル設定を取得"""
        if profile_name in self.config.get('profiles', {}):
            profile = self.config['profiles'][profile_name]
            return {
                'target_size_mb': profile.get('target_size_mb', 45),
                'quality_preset': profile.get('quality_preset', 'medium')
            }
        return None
    
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
        
        # プログレスバーを初期化
        progress_bar = ProgressBar(duration)
        
        # アニメーションスレッドを開始
        animation_thread = threading.Thread(target=progress_bar.animate_spinner)
        animation_thread.daemon = True
        animation_thread.start()
        
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True
        )
        
        # プログレス監視
        stderr_lines = []
        for line in process.stderr:
            stderr_lines.append(line)
            # 時間の進行を取得
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                
                progress_bar.update_progress(current_time)
        
        process.wait()
        
        # アニメーションを停止
        progress_bar.stop()
        animation_thread.join(timeout=0.1)
        
        # 最終プログレスを表示
        final_bar = progress_bar.draw_progress_bar(100)
        print(f"\r{Colors.GREEN}✓{Colors.NC} {final_bar} 100.0% {Colors.GREEN}完了{Colors.NC}")
        
        if process.returncode != 0:
            error_output = '\n'.join(stderr_lines[-10:])  # 最後の10行のみ表示
            print(f"{Colors.RED}エラー: ffmpegの実行に失敗しました{Colors.NC}")
            print(f"Error details: {error_output}")
            sys.exit(1)
    
    def compress_video(self, input_file, output_file, target_size_mb=45, quality_preset='medium'):
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
        
        # 品質プリセットを取得
        preset_config = self.quality_presets.get(quality_preset, self.quality_presets['medium'])
        
        # 目標ビットレートを計算
        target_bitrate = self.calculate_target_bitrate(target_size_mb, duration)
        print(f"{Colors.BLUE}目標ビットレート:{Colors.NC} {target_bitrate}bps")
        print(f"{Colors.BLUE}品質プリセット:{Colors.NC} {quality_preset} (preset: {preset_config['preset']}, crf: {preset_config['crf']})")
        
        print(f"{Colors.YELLOW}圧縮を開始しています...{Colors.NC}")
        
        # 2-pass エンコーディング
        # Pass 1
        cmd_pass1 = [
            'ffmpeg', '-y', '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', str(target_bitrate),
            '-pass', '1',
            '-preset', preset_config['preset'],
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
            '-preset', preset_config['preset'],
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
    
    def batch_compress(self, input_directory, output_directory=None, target_size_mb=45, quality_preset='medium'):
        """ディレクトリ内の全動画ファイルを一括圧縮"""
        input_path = Path(input_directory)
        
        if not input_path.exists() or not input_path.is_dir():
            print(f"{Colors.RED}エラー: ディレクトリ '{input_directory}' が見つかりません{Colors.NC}")
            sys.exit(1)
        
        # 出力ディレクトリの設定
        if output_directory is None:
            output_path = input_path / "compressed"
        else:
            output_path = Path(output_directory)
        
        output_path.mkdir(exist_ok=True)
        
        # 動画ファイルの拡張子
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        
        # 動画ファイルを検索
        video_files = [f for f in input_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in video_extensions]
        
        if not video_files:
            print(f"{Colors.YELLOW}処理対象の動画ファイルが見つかりませんでした{Colors.NC}")
            return
        
        print(f"{Colors.BLUE}バッチ処理開始:{Colors.NC} {len(video_files)}個のファイルを処理します")
        print(f"{Colors.BLUE}入力ディレクトリ:{Colors.NC} {input_directory}")
        print(f"{Colors.BLUE}出力ディレクトリ:{Colors.NC} {output_path}")
        print()
        
        successful = 0
        failed = 0
        
        for i, video_file in enumerate(video_files, 1):
            print(f"{Colors.CYAN}[{i}/{len(video_files)}] 処理中: {video_file.name}{Colors.NC}")
            
            try:
                output_file = output_path / f"{video_file.stem}_compressed.mp4"
                
                # すでに処理済みのファイルがある場合はスキップ
                if output_file.exists():
                    print(f"{Colors.YELLOW}スキップ: {output_file.name} は既に存在します{Colors.NC}")
                    continue
                
                self.compress_video(str(video_file), str(output_file), target_size_mb, quality_preset)
                successful += 1
                print(f"{Colors.GREEN}✅ 完了: {output_file.name}{Colors.NC}")
                
            except Exception as e:
                print(f"{Colors.RED}❌ エラー: {video_file.name} - {str(e)}{Colors.NC}")
                failed += 1
            
            print("-" * 50)
        
        # 結果サマリー
        print(f"{Colors.BLUE}バッチ処理完了{Colors.NC}")
        print(f"{Colors.GREEN}成功: {successful}個{Colors.NC}")
        if failed > 0:
            print(f"{Colors.RED}失敗: {failed}個{Colors.NC}")

def main():
    parser = argparse.ArgumentParser(
        description="Discord用動画圧縮ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python compress_video.py input.mov
  python compress_video.py input.mov output.mp4
  python compress_video.py input.mov -s 300 -q slow
  python compress_video.py --batch /path/to/videos -s 200
        """
    )
    
    parser.add_argument('input_file', nargs='?', help='入力動画ファイル（バッチモード時はディレクトリ）')
    parser.add_argument('output_file', nargs='?', help='出力ファイル名（省略時は自動生成）')
    parser.add_argument('-s', '--size', type=int, default=45, 
                       help='目標サイズをMBで指定（デフォルト: 45MB）')
    parser.add_argument('-q', '--quality', choices=['fast', 'medium', 'slow', 'high'], 
                       default='medium', help='品質プリセット（デフォルト: medium）')
    parser.add_argument('-p', '--profile', help='設定プロファイルを使用（discord, twitter, instagram, youtube_preview）')
    parser.add_argument('--list-profiles', action='store_true', help='利用可能なプロファイルを表示')
    parser.add_argument('--batch', action='store_true', 
                       help='バッチモード: ディレクトリ内の全動画を一括処理')
    parser.add_argument('-o', '--output-dir', help='バッチモード時の出力ディレクトリ')
    
    args = parser.parse_args()
    
    compressor = VideoCompressor()
    
    # プロファイル一覧表示
    if args.list_profiles:
        profiles = compressor.config.get('profiles', {})
        if not profiles:
            print(f"{Colors.YELLOW}設定プロファイルが見つかりません{Colors.NC}")
        else:
            print(f"{Colors.BLUE}利用可能なプロファイル:{Colors.NC}")
            for name, profile in profiles.items():
                desc = profile.get('description', '説明なし')
                size = profile.get('target_size_mb', 'N/A')
                quality = profile.get('quality_preset', 'N/A')
                print(f"  {Colors.GREEN}{name}{Colors.NC}: {desc} (サイズ: {size}MB, 品質: {quality})")
        sys.exit(0)
    
    if not args.input_file:
        parser.print_help()
        sys.exit(1)
    
    # プロファイル設定の適用
    target_size = args.size
    quality_preset = args.quality
    
    if args.profile:
        profile_settings = compressor.get_profile_settings(args.profile)
        if profile_settings:
            target_size = profile_settings['target_size_mb']
            quality_preset = profile_settings['quality_preset']
            print(f"{Colors.BLUE}プロファイル '{args.profile}' を適用しました{Colors.NC}")
        else:
            print(f"{Colors.RED}エラー: プロファイル '{args.profile}' が見つかりません{Colors.NC}")
            print("--list-profiles で利用可能なプロファイルを確認してください")
            sys.exit(1)
    
    # バッチモード
    if args.batch:
        compressor.batch_compress(
            args.input_file, 
            args.output_dir, 
            target_size, 
            quality_preset
        )
    else:
        # 単一ファイルモード
        # 出力ファイル名の生成
        if not args.output_file:
            input_path = Path(args.input_file)
            stem = input_path.stem
            args.output_file = f"{stem}_compressed.mp4"
        
        # 圧縮実行
        compressor.compress_video(args.input_file, args.output_file, target_size, quality_preset)

if __name__ == '__main__':
    main()