#!/bin/bash

# Discord動画圧縮ツール
# 使用法: compress_video <入力ファイル> [出力ファイル]
# 500MB以下に動画を圧縮します

set -e

# 色付き出力用の定数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプメッセージ
show_help() {
    echo -e "${BLUE}Discord動画圧縮ツール${NC}"
    echo ""
    echo "使用法: compress_video <入力ファイル> [出力ファイル]"
    echo ""
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -s, --size     目標サイズをMBで指定 (デフォルト: 45MB)"
    echo ""
    echo "例:"
    echo "  compress_video input.mov"
    echo "  compress_video input.mov output.mp4"
    echo "  compress_video input.mov -s 300"
}

# ffmpegの存在確認
check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${RED}エラー: ffmpegがインストールされていません${NC}"
        echo "以下のコマンドでインストールしてください:"
        echo "  macOS: brew install ffmpeg"
        echo "  Ubuntu: sudo apt install ffmpeg"
        echo "  Windows: https://ffmpeg.org/download.html"
        exit 1
    fi
}

# ファイルサイズを取得（MB単位）
get_file_size_mb() {
    local file="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        stat -f%z "$file" | awk '{print $1/1024/1024}'
    else
        # Linux
        stat -c%s "$file" | awk '{print $1/1024/1024}'
    fi
}

# 動画の長さを取得（秒）
get_video_duration() {
    local file="$1"
    ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file"
}

# 目標ビットレートを計算
calculate_target_bitrate() {
    local target_size_mb="$1"
    local duration_sec="$2"
    
    # bcを使って浮動小数点演算を実行
    local target_size_bits=$(echo "$target_size_mb * 8 * 1024 * 1024" | bc)
    local target_bitrate=$(echo "scale=0; $target_size_bits / $duration_sec" | bc)
    
    # 音声ビットレート（128kbps）を差し引く
    local audio_bitrate=128000
    local video_bitrate=$(echo "$target_bitrate - $audio_bitrate" | bc)
    
    # 最小ビットレートを確保
    if (( $(echo "$video_bitrate < 500000" | bc -l) )); then
        video_bitrate=500000
    fi
    
    echo ${video_bitrate%.*}  # 整数部分のみ取得
}

# メイン処理
main() {
    local input_file=""
    local output_file=""
    local target_size_mb=45
    
    # 引数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--size)
                target_size_mb="$2"
                shift 2
                ;;
            -*)
                echo -e "${RED}エラー: 不明なオプション $1${NC}"
                show_help
                exit 1
                ;;
            *)
                if [ -z "$input_file" ]; then
                    input_file="$1"
                elif [ -z "$output_file" ]; then
                    output_file="$1"
                fi
                shift
                ;;
        esac
    done
    
    # 入力ファイルのチェック
    if [ -z "$input_file" ]; then
        echo -e "${RED}エラー: 入力ファイルが指定されていません${NC}"
        show_help
        exit 1
    fi
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}エラー: ファイル '$input_file' が見つかりません${NC}"
        exit 1
    fi
    
    # 出力ファイル名の生成
    if [ -z "$output_file" ]; then
        local basename=$(basename "$input_file" | sed 's/\.[^.]*$//')
        local extension="${input_file##*.}"
        output_file="${basename}_compressed.mp4"
    fi
    
    # ffmpegの存在確認
    check_ffmpeg
    
    # 現在のファイルサイズを確認
    local current_size_mb=$(get_file_size_mb "$input_file")
    echo -e "${BLUE}入力ファイル:${NC} $input_file"
    echo -e "${BLUE}現在のサイズ:${NC} ${current_size_mb}MB"
    echo -e "${BLUE}目標サイズ:${NC} ${target_size_mb}MB"
    
    # 既に目標サイズ以下の場合
    if (( $(echo "$current_size_mb <= $target_size_mb" | bc -l) )); then
        echo -e "${GREEN}ファイルは既に目標サイズ以下です。コピーのみ実行します。${NC}"
        cp "$input_file" "$output_file"
        echo -e "${GREEN}完了: $output_file${NC}"
        exit 0
    fi
    
    # 動画の長さを取得
    local duration=$(get_video_duration "$input_file")
    echo -e "${BLUE}動画の長さ:${NC} ${duration}秒"
    
    # 目標ビットレートを計算
    local target_bitrate=$(calculate_target_bitrate $target_size_mb $duration)
    echo -e "${BLUE}目標ビットレート:${NC} ${target_bitrate}bps"
    
    echo -e "${YELLOW}圧縮を開始しています...${NC}"
    
    # 2-pass エンコーディングで圧縮
    # Pass 1
    echo -e "${YELLOW}Pass 1/2: 分析中...${NC}"
    ffmpeg -y -i "$input_file" \
        -c:v libx264 \
        -b:v ${target_bitrate} \
        -pass 1 \
        -preset medium \
        -f null /dev/null 2>/dev/null
    
    # Pass 2
    echo -e "${YELLOW}Pass 2/2: エンコード中...${NC}"
    ffmpeg -y -i "$input_file" \
        -c:v libx264 \
        -b:v ${target_bitrate} \
        -pass 2 \
        -preset medium \
        -c:a aac \
        -b:a 128k \
        "$output_file"
    
    # ログファイルを削除
    rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree
    
    # 結果を表示
    local output_size_mb=$(get_file_size_mb "$output_file")
    echo ""
    echo -e "${GREEN}圧縮完了!${NC}"
    echo -e "${BLUE}出力ファイル:${NC} $output_file"
    echo -e "${BLUE}圧縮後サイズ:${NC} ${output_size_mb}MB"
    echo -e "${BLUE}圧縮率:${NC} $(echo "scale=1; 100 - ($output_size_mb * 100 / $current_size_mb)" | bc)%"
    
    # Discord制限チェック
    if (( $(echo "$output_size_mb <= 50" | bc -l) )); then
        echo -e "${GREEN}✅ Discordにアップロード可能です${NC}"
    else
        echo -e "${YELLOW}⚠️  まだ50MBを超えています。さらに圧縮が必要です${NC}"
    fi
}

main "$@"