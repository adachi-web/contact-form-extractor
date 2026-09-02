# 🔍 問い合わせフォームURL自動抽出 - Streamlit Cloud版

営業リストのHP URLから、**問い合わせフォームURL**を自動抽出・検証するWebアプリです。

クラウド上で実行されるため、PC を起動し続ける必要がありません！

---

## 🚀 クイックスタート

### 1️⃣ GitHub にリポジトリを作成

```bash
# ローカルで作業
mkdir contact-form-extractor
cd contact-form-extractor
git init

# このファイルたちをコピー
# - streamlit_app.py
# - requirements.txt
# - README.md
# - .gitignore

git add .
git commit -m "Initial commit: Streamlit contact form extractor"
git remote add origin https://github.com/YOUR_USERNAME/contact-form-extractor.git
git branch -M main
git push -u origin main
```

### 2️⃣ Streamlit Share でデプロイ

1. https://share.streamlit.io/ にアクセス
2. GitHub アカウントでログイン
3. 「New app」をクリック
4. リポジトリ選択:
   - Repository: `contact-form-extractor`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
5. 「Deploy」をクリック

**→ 自動でクラウドにデプロイされます！** ☁️

---

## 💻 ローカルで試す

### セットアップ

```bash
# Python 3.8 以上が必要
python --version

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 実行

```bash
streamlit run streamlit_app.py
```

ブラウザで `http://localhost:8501` が自動で開きます。

---

## 📋 使い方

### 入力ファイル（CSV）の形式

- **必須**: HP URL が含まれた列
- 例:

```csv
会社名,業種,ホームページURL
A社,建設,https://example-a.com
B社,製造,https://example-b.com
C社,小売,https://example-c.com
```

### 処理内容

1. **HP URL列の自動検出** → 「URL」「ホームページ」などのキーワードから自動判定
2. **フォームURLの自動抽出** → HTML スクレイピングで探す
3. **有効性チェック** → 404 や無効なリンクを除去
4. **重複削除** → 同じドメインの重複をクリア
5. **結果ダウンロード** → CSV で出力

### 出力ファイル

```csv
会社名,業種,ホームページURL,フォームURL
A社,建設,https://example-a.com,https://example-a.com/contact
B社,製造,https://example-b.com,https://example-b.com/inquiry
C社,小売,https://example-c.com,
```

---

## ⚡ 処理時間

| ファイルサイズ | 予想時間 |
|---|---|
| 30 件 | 30秒～1分 |
| 100 件 | 2～3分 |
| 300 件 | 5～10分 |

※ サイトの読み込み速度に依存します

---

## 🔧 トラブルシューティング

### Q. Streamlit Share でエラーが出る

**A.** 以下を確認:
- `requirements.txt` に必要なパッケージが全部入っているか
- `streamlit_app.py` の Main file path が正しいか
- GitHub にコミットしているか

### Q. フォームURL が取得できない

**A.** 以下の理由が考えられます:
- サイトが JavaScript で動的に読み込んでいる（Playwright が無効）
- `robots.txt` でブロックされている
- フォームが別ドメインのサービスを使用している

### Q. 処理が途中で止まる

**A.** Streamlit Share の無料枠の制限（数時間以内）に達した可能性があります。
少し待ってから再実行してください。

---

## 🛠️ カスタマイズ

### 並列処理数を変更

Streamlit Share 使用時は `MAX_WORKERS = 5` をおすすめします。
ローカルなら `MAX_WORKERS = 10` で高速化できます。

```python
# streamlit_app.py の上部
MAX_WORKERS = 5  # ここを変更
```

### キーワードを追加

抽出の精度を上げたい場合:

```python
CONTACT_KEYWORDS = [
    'お問い合わせ', 'お問合わせ', ...
    # ここに新しいキーワード追加
]
```

---

## 📊 営業フロー連携

### Sales Boost への入力

1. Streamlit で CSV ダウンロード
2. Sales Boost にインポート
3. 営業3人で同時利用可能 ✅

### スケジュール実行（自動化）

GitHub Actions を使えば、毎週決まった時間に自動実行できます。
別途セットアップが必要です。

---

## 🎯 こんな時に便利

✅ 営業リスト 30～300 件の一括処理  
✅ PC を起動し続けたくない  
✅ チーム全体で共有したい  
✅ 無料で運用したい  

---

## 📝 ライセンス

自由に使用・カスタマイズ可能です。

---

## 💬 Feedback

改善提案や不具合報告は GitHub Issues にお願いします。

---

**Made with ❤️ for HYN株式会社**
