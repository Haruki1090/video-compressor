# Discord動画圧縮ツール

Discord の 500MB 制限に対応した動画圧縮ツールです。シェルスクリプト版と Python 版の両方を提供しています。

## 特徴

- 🎯 **500MB以下に自動圧縮**: Discordにアップロード可能なサイズに調整
- 📊 **品質維持**: 2-pass エンコーディングで効率的な圧縮
- 🚀 **簡単操作**: コマンド一つで実行可能
- 📈 **進捗表示**: リアルタイムでエンコード進行状況を表示
- 🎛️ **カスタマイズ可能**: 目標サイズの調整が可能

## 必要な環境

- **ffmpeg**: 動画のエンコードに使用
- **Python 3.x**: Python版を使用する場合
- **bash/zsh**: シェルスクリプト版を使用する場合

## インストール

### 1. ffmpeg のインストール

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### 2. プロジェクトのセットアップ

1. 全てのファイルを `~/StudioProjects/video-compressor` に配置
2. セットアップスクリプトを実行:

```bash
chmod +x setup.sh
./setup.sh
```

3. 新しいターミナルを開くか、設定を再読み込み:

```bash
source ~/.zshrc  # zshの場合
# または
source ~/.bashrc  # bashの場合
```

## 使用方法

### シェルスクリプト版（推奨）

```bash
# 基本的な使用法
compress_video input.mov

# 出力ファイル名を指定
compress_video input.mov output.mp4

# 目標サイズを指定（MB）
compress_video input.mov -s 300

# ヘルプを表示
compress_video --help
```

### Python版

```bash
# 基本的な使用法
compress_video_py input.mov

# 出力ファイル名を指定
compress_video_py input.mov output.mp4

# 目標サイズを指定（MB）
compress_video_py input.mov -s 300

# ヘルプを表示
compress_video_py --help
```

## 使用例

### 基本的な圧縮

```bash
$ compress_video screen_recording.mov
入力ファイル: screen_recording.mov
現在のサイズ: 1250.5MB
目標サイズ: 450MB
動画の長さ: 180.5秒
目標ビットレート: 19800000bps
圧縮を開始しています...
Pass 1/2: 分析中...
Pass 2/2: エンコード中...
進行状況: 100.0%

圧縮完了!
出力ファイル: screen_recording_compressed.mp4
圧縮後サイズ: 445.2MB
圧縮率: 64.4%
✅ Discordにアップロード可能です
```

### 小さいサイズでの圧縮

```bash
$ compress_video large_video.mp4 -s 200
# 200MBを目標に圧縮
```

## ファイル構成

```
~/StudioProjects/video-compressor/
├── compress_video.sh      # シェルスクリプト版メイン
├── compress_video.py      # Python版メイン
├── setup.sh              # セットアップスクリプト
└── README.md             # このファイル
```

## 技術仕様

### エンコード設定

- **コーデック**: H.264 (libx264)
- **音声**: AAC 128kbps
- **エンコード方式**: 2-pass
- **プリセット**: medium（品質と速度のバランス）

### ビットレート計算

```
目標ビットレート = (目標サイズ × 8 × 1024 × 1024) ÷ 動画の長さ(秒) - 音声ビットレート
```

## トラブルシューティング

### ffmpeg が見つからない

```bash
# インストール確認
which ffmpeg

# パスの確認
echo $PATH
```

### 権限エラー

```bash
# 実行権限を付与
chmod +x ~/StudioProjects/video-compressor/compress_video.sh
chmod +x ~/StudioProjects/video-compressor/compress_video.py
```

### コマンドが見つからない

1. 新しいターミナルを開く
2. PATH設定を確認:

```bash
echo $PATH | grep StudioProjects
```

3. 手動でPATHを設定:

```bash
export PATH=\"$PATH:$HOME/StudioProjects/video-compressor\"
```

### 圧縮に失敗する場合

1. 入力ファイルが破損していないか確認
2. ディスク容量が十分にあるか確認
3. ffmpegが正常にインストールされているか確認

```bash
ffmpeg -version
```

## よくある質問

**Q: 圧縮にはどれくらい時間がかかりますか？**
A: 動画の長さ、解像度、CPUの性能により異なりますが、通常は元の動画の長さの0.5〜2倍程度です。

**Q: 画質はどれくらい劣化しますか？**
A: 2-passエンコーディングを使用しているため、ファイルサイズに対して最適な品質を維持します。圧縮率が高いほど画質への影響は大きくなります。

**Q: 対応している動画フォーマットは？**
A: ffmpegが対応している全てのフォーマット（MP4, MOV, AVI, MKV など）に対応しています。

**Q: 既に500MB以下のファイルはどうなりますか？**
A: ファイルサイズをチェックし、既に目標サイズ以下の場合はコピーのみ実行します。

## ライセンス

このツールはMITライセンスの下で提供されています。

## 貢献

バグ報告や機能改善の提案は Issues までお願いします。# video-compressor
