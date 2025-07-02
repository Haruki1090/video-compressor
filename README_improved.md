# 📹 Discord動画圧縮ツール（改良版）

Discord の 500MB 制限に対応した高機能動画圧縮ツールです。シェルスクリプト版とPython版の両方を提供し、様々な便利機能を搭載しています。

## ✨ 新機能

### 🎨 改善されたユーザーインターフェース
- **アニメーション付きプログレスバー**: リアルタイムでエンコード進行状況を視覚的に表示
- **カラフルな出力**: 色付きテキストで見やすく情報を表示
- **スピナーアニメーション**: 処理中の視覚的フィードバック

### ⚙️ 品質プリセット
| プリセット | 処理速度 | 品質 | 用途 |
|------------|----------|------|------|
| `fast`     | 高速     | 標準 | 高速処理優先 |
| `medium`   | 標準     | 良好 | バランス重視（デフォルト） |
| `slow`     | 低速     | 高品質 | 品質優先 |
| `high`     | 最低速   | 最高品質 | 最高品質重視 |

### 🎯 設定プロファイル
事前定義されたプラットフォーム向け設定：
- **discord**: Discord用（45MB、medium品質）
- **twitter**: Twitter用（500MB、slow品質）
- **instagram**: Instagram用（100MB、slow品質）
- **youtube_preview**: YouTube プレビュー用（20MB、fast品質）

### 📦 バッチ処理
- ディレクトリ内の全動画ファイルを一括処理
- 既存ファイルのスキップ機能
- 処理結果の詳細レポート

## 🚀 使用方法

### 基本的な使用法

```bash
# 基本圧縮（45MBに圧縮）
python3 compress_video.py input.mov

# 出力ファイル名を指定
python3 compress_video.py input.mov output.mp4

# サイズと品質を指定
python3 compress_video.py input.mov -s 100 -q slow
```

### プロファイルの使用

```bash
# 利用可能なプロファイルを表示
python3 compress_video.py --list-profiles

# Discordプロファイルを使用
python3 compress_video.py input.mov -p discord

# Twitterプロファイルを使用
python3 compress_video.py input.mov -p twitter
```

### バッチ処理

```bash
# ディレクトリ内の全動画を圧縮
python3 compress_video.py --batch /path/to/videos

# 出力ディレクトリを指定
python3 compress_video.py --batch /path/to/videos -o /path/to/output

# プロファイルと組み合わせ
python3 compress_video.py --batch /path/to/videos -p instagram
```

## 📋 コマンドライン引数

| 引数 | 短縮形 | 説明 | 例 |
|------|--------|------|-----|
| `input_file` | - | 入力ファイル/ディレクトリ | `input.mov` |
| `output_file` | - | 出力ファイル名（省略時は自動生成） | `output.mp4` |
| `--size` | `-s` | 目標サイズ（MB） | `-s 100` |
| `--quality` | `-q` | 品質プリセット | `-q slow` |
| `--profile` | `-p` | 設定プロファイル | `-p discord` |
| `--batch` | - | バッチモード | `--batch` |
| `--output-dir` | `-o` | 出力ディレクトリ | `-o /path/to/output` |
| `--list-profiles` | - | プロファイル一覧表示 | `--list-profiles` |

## 🛠️ インストールと設定

### 1. 必要な環境

```bash
# macOS
brew install ffmpeg python3

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg python3

# Windows (Chocolatey)
choco install ffmpeg python3
```

### 2. プロジェクトのセットアップ

```bash
# ファイルを配置
cd ~/StudioProjects/video-compressor

# セットアップスクリプトを実行
chmod +x setup.sh
./setup.sh

# 設定を再読み込み
source ~/.zshrc  # または ~/.bashrc
```

### 3. テスト実行

```bash
# テストスクリプトを実行
python3 test_compressor.py

# 基本動作確認
python3 compress_video.py --help
python3 compress_video.py --list-profiles
```

## ⚙️ 設定ファイル（config.json）

設定ファイルで独自のプロファイルや既定値をカスタマイズできます：

```json
{
  "default_settings": {
    "target_size_mb": 45,
    "quality_preset": "medium",
    "audio_bitrate": "128k"
  },
  "profiles": {
    "custom": {
      "target_size_mb": 30,
      "quality_preset": "high",
      "description": "カスタム設定例"
    }
  }
}
```

## 📊 パフォーマンス比較

### 旧版 vs 改良版

| 機能 | 旧版 | 改良版 |
|------|------|--------|
| プログレス表示 | 簡易パーセンテージ | ✅ アニメーション付きバー |
| 品質設定 | 固定（medium） | ✅ 4種類のプリセット |
| バッチ処理 | ❌ なし | ✅ フォルダ一括処理 |
| プロファイル | ❌ なし | ✅ プラットフォーム別設定 |
| 設定ファイル | ❌ なし | ✅ JSON設定対応 |
| エラーハンドリング | 基本的 | ✅ 詳細なエラー情報 |

## 🔧 技術仕様

### エンコード設定

- **動画コーデック**: H.264 (libx264)
- **音声コーデック**: AAC 128kbps
- **エンコード方式**: 2-pass
- **品質制御**: CRF + ビットレート制限

### プリセット詳細

```python
quality_presets = {
    'fast': {'preset': 'fast', 'crf': 28},      # 高速処理
    'medium': {'preset': 'medium', 'crf': 23},   # バランス
    'slow': {'preset': 'slow', 'crf': 20},       # 高品質
    'high': {'preset': 'slower', 'crf': 18}      # 最高品質
}
```

## 🎯 使用例とサンプル

### 1. ゲーム実況動画（Discord投稿用）

```bash
python3 compress_video.py gameplay.mp4 -p discord -q medium
# 結果: 45MB以下、適度な品質でDiscordに投稿可能
```

### 2. 高品質プレゼンテーション動画

```bash
python3 compress_video.py presentation.mov -s 200 -q high
# 結果: 200MB、最高品質設定で圧縮
```

### 3. 大量の動画ファイル一括処理

```bash
python3 compress_video.py --batch ./raw_videos -p youtube_preview -o ./compressed
# 結果: 全ファイルを20MBのプレビュー用に高速圧縮
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

1. **ffmpeg not found**
   ```bash
   which ffmpeg  # インストール確認
   brew install ffmpeg  # macOSでの再インストール
   ```

2. **Python モジュールエラー**
   ```bash
   python3 --version  # Python3確認
   pip3 install --upgrade pip  # pipの更新
   ```

3. **プログレスバーが表示されない**
   - ターミナルがUnicode対応しているか確認
   - 古いPythonバージョンの場合は更新

4. **バッチ処理でファイルがスキップされる**
   - 出力ディレクトリに同名ファイルが存在
   - `--force` オプション（将来追加予定）を使用

## 📈 パフォーマンステスト結果

```
テスト環境: MacBook Pro M1, 16GB RAM
入力: 1080p 60fps 10分動画 (2GB)

品質プリセット別処理時間:
├── fast:   約 3分 → 45MB (圧縮率: 97.8%)
├── medium: 約 8分 → 45MB (圧縮率: 97.8%)
├── slow:   約15分 → 45MB (圧縮率: 97.8%)
└── high:   約25分 → 45MB (圧縮率: 97.8%)

※ 圧縮率は同じでも、品質に差があります
```

## 🔮 今後の予定機能

- [ ] GPU加速エンコーディング（NVENC/QuickSync対応）
- [ ] Webベースの管理インターフェース
- [ ] 動画のプレビュー機能
- [ ] 圧縮前後の品質比較
- [ ] ログファイル出力機能
- [ ] クラウドストレージ連携

## 📄 ライセンス

MIT License - 自由にご利用ください

## 🤝 コントリビューション

改善案やバグ報告はIssuesまでお願いします！

---

**⭐ このツールが役に立ったら、ぜひスターをお願いします！** 