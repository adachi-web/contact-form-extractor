# 🚀 Streamlit Share へのデプロイ手順（完全ガイド）

このガイドに従えば、**5分で Streamlit Share に公開できます！**

---

## 📋 事前準備

### ✅ 必要なもの

- GitHub アカウント（無料で OK）
- 今回のコード 4ファイル:
  - `streamlit_app.py`
  - `requirements.txt`
  - `README.md`
  - `.gitignore`

---

## ステップ 1: GitHub リポジトリを作成

### 1-1. GitHub で新規リポジトリ作成

1. https://github.com/new にアクセス
2. Repository name: **`contact-form-extractor`**（任意の名前OK）
3. Public にチェック（Streamlit Share は Public リポジトリが必須）
4. 「Create repository」をクリック

### 1-2. ローカルで準備

```bash
# フォルダ作成
mkdir contact-form-extractor
cd contact-form-extractor

# Git初期化
git init

# 今回のファイル 4つをこのフォルダにコピー
# - streamlit_app.py
# - requirements.txt
# - README.md
# - .gitignore
```

### 1-3. GitHub にプッシュ

```bash
# ファイルをステージ
git add .

# コミット
git commit -m "Initial commit: Streamlit contact form extractor"

# リモート追加（YOUR_USERNAME をあなたの GitHub ユーザー名に置き換え）
git remote add origin https://github.com/YOUR_USERNAME/contact-form-extractor.git

# ブランチ名を main に変更
git branch -M main

# プッシュ
git push -u origin main
```

**→ GitHub にコードがアップロードされました！** ✅

---

## ステップ 2: Streamlit Share でデプロイ

### 2-1. Streamlit Share にログイン

1. https://share.streamlit.io/ にアクセス
2. 「Sign in with GitHub」をクリック
3. GitHub アカウントでログイン
4. Streamlit がリポジトリへのアクセスを求めてきたら「Authorize」

### 2-2. アプリをデプロイ

1. Streamlit Share のダッシュボードで「New app」をクリック
2. 以下を入力:
   - **Repository**: `YOUR_USERNAME/contact-form-extractor`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
3. 「Deploy」をクリック

**→ デプロイが開始されます！** 🚀

### 2-3. デプロイ完了を待つ

- 初回デプロイは 2～3 分かかります
- ログを見ながら待機します
- 「Running」と表示されたら完了！

```
Your app is ready! 🎉
streamlit.app で公開されました
```

---

## ✨ 使用開始！

アプリが起動したら:

1. CSV ファイルをアップロード
2. 「処理開始」ボタンをクリック
3. 完了したらダウンロード

**→ クラウド上で自動実行されます！** ☁️

---

## 📱 シェアする

### 営業チーム全員でアクセス可能

```
https://your-username-contact-form-extractor.streamlit.app/
```

↑ この URL を営業3人に共有すれば、全員がブラウザで使えます！

---

## 🔄 更新・カスタマイズ

コードを変更したい場合：

```bash
# ローカルで編集
# 例）キーワード追加、色変更など

# コミット＆プッシュ
git add .
git commit -m "Update: キーワード追加"
git push origin main
```

→ **自動で Streamlit が再デプロイしてくれます！**

---

## 🆘 よくあるエラー

### ❌ "Repository not found"

**原因**: GitHub リポジトリが見つからない

**対策**:
- リポジトリを **Public** にしているか確認
- Repository 名が正しいか確認
- GitHub にプッシュできているか確認

### ❌ "ModuleNotFoundError"

**原因**: `requirements.txt` に記載漏れ

**対策**:
- `requirements.txt` に必要なパッケージが全部入っているか確認
- 文法（バージョン指定）が正しいか確認

```
# 例：
streamlit==1.28.1
pandas==2.1.3
requests==2.31.0
beautifulsoup4==4.12.2
```

### ❌ "Execution timeout"

**原因**: 処理時間が長すぎる（300件以上）

**対策**:
- `MAX_WORKERS` を 3 に下げる
- 複数回に分けて処理する
- Premium プランへアップグレード（オプション）

---

## 💰 コスト（完全無料！）

| 項目 | 無料枠 | 料金 |
|---|---|---|
| GitHub | ∞ | $0 |
| Streamlit Share | 月 1GB・3アプリまで | $0 |
| 合計 | - | **$0 🎉** |

---

## 📊 無料枠の制限

Streamlit Share の無料枠:
- **ストレージ**: 1GB（ログ含む）
- **アプリ数**: 3個まで同時公開
- **実行時間**: 各アプリ 72時間/month（つまり常時動作OK）
- **CPU/メモリ**: 共有リソース

→ **営業ツールとしては十分すぎるスペック！** 💪

---

## 🎯 このあとやること

1. ✅ GitHub にコミット
2. ✅ Streamlit Share でデプロイ
3. 📱 営業チームに URL 共有
4. 🧪 テスト（CSV 30件でトライ）
5. 🚀 Sales Boost 連携

---

## 🔗 参考リンク

- [Streamlit 公式ドキュメント](https://docs.streamlit.io/)
- [Streamlit Share FAQ](https://docs.streamlit.io/streamlit-community-cloud/get-started/share-your-app)
- [GitHub Pages](https://pages.github.com/)

---

**🎉 デプロイ完了！**

ともひろ、これであなたの営業システムは完全クラウド化されました！
