#!/bin/bash

# Discord動画圧縮ツール セットアップスクリプト
# このスクリプトは~/StudioProjects/video-compressor に配置し、
# PATHを設定してどこからでも使えるようにします

set -e

# 色付き出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 設定
PROJECT_DIR="$HOME/StudioProjects/video-compressor"
SCRIPT_NAME="compress_video"
PYTHON_SCRIPT_NAME="compress_video.py"

echo -e "${BLUE}Discord動画圧縮ツール セットアップ${NC}"
echo "========================================"

# StudioProjectsディレクトリが存在しない場合は作成
if [ ! -d "$HOME/StudioProjects" ]; then
    echo -e "${YELLOW}StudioProjects ディレクトリを作成しています...${NC}"
    mkdir -p "$HOME/StudioProjects"
fi

# プロジェクトディレクトリを作成
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}プロジェクトディレクトリを作成しています...${NC}"
    mkdir -p "$PROJECT_DIR"
fi

# 現在のスクリプトの場所を確認
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ファイルをプロジェクトディレクトリにコピー
echo -e "${YELLOW}ファイルをコピーしています...${NC}"

if [ -f "$CURRENT_DIR/compress_video.sh" ]; then
    # 同じファイルの場合のエラーを無視
    cp "$CURRENT_DIR/compress_video.sh" "$PROJECT_DIR/" 2>/dev/null || true
    chmod +x "$PROJECT_DIR/compress_video.sh"
    echo "✅ compress_video.sh をコピー/確認しました"
else
    echo -e "${RED}警告: compress_video.sh が見つかりません${NC}"
fi

if [ -f "$CURRENT_DIR/compress_video.py" ]; then
    # 同じファイルの場合のエラーを無視
    cp "$CURRENT_DIR/compress_video.py" "$PROJECT_DIR/" 2>/dev/null || true
    chmod +x "$PROJECT_DIR/compress_video.py"
    echo "✅ compress_video.py をコピー/確認しました"
else
    echo -e "${RED}警告: compress_video.py が見つかりません${NC}"
fi

if [ -f "$CURRENT_DIR/README.md" ]; then
    # 同じファイルの場合のエラーを無視
    cp "$CURRENT_DIR/README.md" "$PROJECT_DIR/" 2>/dev/null || true
    echo "✅ README.md をコピー/確認しました"
fi

# ffmpegの存在確認
echo -e "${YELLOW}依存関係をチェックしています...${NC}"
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg がインストールされています"
else
    echo -e "${RED}❌ ffmpeg がインストールされていません${NC}"
    echo "以下のコマンドでインストールしてください:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
fi

if command -v python3 &> /dev/null; then
    echo "✅ Python3 がインストールされています"
else
    echo -e "${RED}❌ Python3 がインストールされていません${NC}"
fi

# シェルの設定ファイルを特定
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    else
        SHELL_CONFIG="$HOME/.bashrc"
    fi
fi

# PATH設定を追加
if [ -n "$SHELL_CONFIG" ]; then
    echo -e "${YELLOW}PATH設定を追加しています...${NC}"
    
    # 既存の設定をチェック
    if grep -q "# Discord Video Compressor" "$SHELL_CONFIG" 2>/dev/null; then
        echo "⚠️  PATH設定は既に存在します"
    else
        # PATH設定を追加
        cat >> "$SHELL_CONFIG" << EOF

# Discord Video Compressor
export PATH="\$PATH:$PROJECT_DIR"
alias compress_video="$PROJECT_DIR/compress_video.sh"
alias compress_video_py="python3 $PROJECT_DIR/compress_video.py"
EOF
        echo "✅ PATH設定を $SHELL_CONFIG に追加しました"
        echo -e "${BLUE}注意: 新しいターミナルを開くか、以下のコマンドを実行してください:${NC}"
        echo "source $SHELL_CONFIG"
    fi
else
    echo -e "${YELLOW}シェル設定ファイルが特定できませんでした${NC}"
    echo "手動でPATHを設定してください:"
    echo "export PATH=\"\$PATH:$PROJECT_DIR\""
fi

echo ""
echo -e "${GREEN}セットアップ完了!${NC}"
echo "========================================"
echo -e "${BLUE}使用方法:${NC}"
echo "  compress_video input.mov              # シェルスクリプト版"
echo "  compress_video_py input.mov           # Python版"
echo "  compress_video input.mov output.mp4   # 出力ファイル名指定"
echo "  compress_video input.mov -s 300       # 目標サイズ指定"
echo ""
echo -e "${BLUE}詳細な使用方法は以下を参照してください:${NC}"
echo "  cat $PROJECT_DIR/README.md"
echo ""

# 新しいターミナルでテストするよう促す
echo -e "${YELLOW}新しいターミナルを開いて以下のコマンドでテストしてください:${NC}"
echo "  compress_video --help"