"""
問い合わせフォームURL抽出 - Streamlit版
==========================================
GitHub + Streamlit Share で クラウド実行するWebアプリ

使い方:
  1. GitHub にこのファイルを push
  2. Streamlit Share (https://share.streamlit.io/) で
     自分のリポジトリを選択してデプロイ
  3. Webブラウザで実行
"""

import streamlit as st
import pandas as pd
import os
import re
import json
import random
import warnings
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import tempfile

warnings.filterwarnings('ignore')

# ============================================================
# 設定
# ============================================================
MAX_WORKERS = 5  # Streamlit Shareは並列数控えめに
TIMEOUT = 10
RETRY_COUNT = 1
USE_PLAYWRIGHT = False  # Streamlit Shareではrequestsのみ推奨

# ============================================================

# ページ設定
st.set_page_config(
    page_title="フォームURL抽出ツール",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 問い合わせフォームURL自動抽出")
st.markdown("""
営業リストのHP URLから、**問い合わせフォームURL**を自動抽出・検証するツールです。
CSVをアップロードするだけで、クラウド上で高速処理！
""")

# ============================================================
# ユーティリティ関数
# ============================================================

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]

CONTACT_KEYWORDS = [
    'お問い合わせ', 'お問合わせ', 'お問合せ', '問い合わせ', '問合わせ', '問合せ',
    'ご連絡', 'ご相談', 'ご依頼', 'お見積', '資料請求', 'メールフォーム',
    'フォーム', 'ご意見', 'ご要望', 'ご質問', 'お申し込み', 'お申込み',
    'contact', 'inquiry', 'enquiry', 'message', 'request',
]

CONTACT_URL_PATTERNS = [
    r'/contact', r'/toiawase', r'/inquiry', r'/enquiry',
    r'/form[/\.]', r'/mail[/\.]', r'/question', r'/feedback',
]

EXTERNAL_FORM_DOMAINS = [
    'form.run', 'formrun.com', 'docs.google.com', 'forms.gle',
    'tayori.com', 'mailform.jp', 'formzu.net', 'ws.formzu.net',
]

EXCLUDE_DOMAINS = [
    'twitter.com', 'x.com', 'instagram.com', 'facebook.com',
    'youtube.com', 'linkedin.com', 'google.com', 'yahoo.co.jp',
]


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }


def get_domain(url):
    if not url or pd.isna(url):
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        if '@' in url or ',' in url:
            return None
        url = 'https://' + url
    try:
        return urlparse(url).netloc.lower().removeprefix('www.')
    except Exception:
        return None


def is_valid_form_url(url):
    """フォームURLの基本的な妥当性チェック"""
    if not url or pd.isna(url):
        return False
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        return False
    try:
        p = urlparse(url)
        if not p.netloc:
            return False
        if any(bad in p.netloc for bad in EXCLUDE_DOMAINS):
            return False
        return True
    except Exception:
        return False


def check_url_alive(url):
    """URLが生きているか確認"""
    try:
        resp = requests.head(url, headers=get_headers(), timeout=5, allow_redirects=True)
        return resp.status_code < 400
    except Exception:
        try:
            resp = requests.get(url, headers=get_headers(), timeout=5, allow_redirects=True)
            return resp.status_code < 400
        except Exception:
            return False


def find_contact_url_requests(site_url):
    """requestsでフォームURLを探す"""
    if not site_url or pd.isna(site_url):
        return None
    
    site_url = str(site_url).strip()
    if not site_url.startswith(('http://', 'https://')):
        site_url = 'https://' + site_url
    
    try:
        resp = requests.get(site_url, headers=get_headers(), timeout=TIMEOUT, allow_redirects=True)
        if resp.status_code >= 400:
            return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        site_domain = get_domain(site_url)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # 全角文字チェック（スキップ）
            if any(ord(c) > 127 for c in href):
                continue
            
            # キーワードマッチ
            if any(kw.lower() in text for kw in CONTACT_KEYWORDS):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
            
            # URLパターンマッチ
            if any(re.search(pattern, href, re.IGNORECASE) for pattern in CONTACT_URL_PATTERNS):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
            
            # 外部フォームサービス
            if any(domain in href for domain in EXTERNAL_FORM_DOMAINS):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
        
        return None
    
    except Exception as e:
        return None


def find_contact_url(site_url):
    """フォームURL検索（メイン）"""
    result = find_contact_url_requests(site_url)
    if result:
        return result
    
    for _ in range(RETRY_COUNT):
        result = find_contact_url_requests(site_url)
        if result:
            return result
    
    return None


def process_row(args):
    """1行処理"""
    idx, site_url, existing_form_url = args
    if existing_form_url and str(existing_form_url).strip() and str(existing_form_url).strip() != 'nan':
        return idx, existing_form_url
    contact_url = find_contact_url(site_url)
    return idx, contact_url


def detect_url_column(df):
    """HP URL列を自動検出"""
    URL_COLUMN_KEYWORDS = ['url', 'URL', 'ホームページ', 'hp', 'HP', 'サイト', 'ウェブ', 'web']
    FORM_COLUMN_KEYWORDS = ['フォーム', '問い合わせ', 'contact', 'form']
    
    cols = list(df.columns)
    for c in cols:
        col_str = str(c).lower()
        if any(k.lower() in col_str for k in FORM_COLUMN_KEYWORDS):
            continue
        if any(k.lower() in col_str for k in URL_COLUMN_KEYWORDS):
            return c
    
    # ヒューリスティック
    best_col = None
    best_ratio = 0.0
    sample_size = min(50, len(df))
    for c in cols:
        sample = df[c].dropna().head(sample_size).astype(str)
        url_count = sample.str.match(r'^https?://', na=False).sum()
        ratio = url_count / max(len(sample), 1)
        if ratio > best_ratio and ratio > 0.3:
            best_ratio = ratio
            best_col = c
    
    return best_col or cols[0]


def detect_form_column(df):
    """フォームURL列を自動検出"""
    FORM_COLUMN_KEYWORDS = ['フォーム', '問い合わせ', '問合', 'contact', 'form', 'inquiry']
    cols = list(df.columns)
    for c in cols:
        if any(k.lower() in str(c).lower() for k in FORM_COLUMN_KEYWORDS):
            return c
    return None


def process_csv(df, progress_bar, status_text):
    """CSVを処理してフォームURLを抽出"""
    
    # 列検出
    col_url = detect_url_column(df)
    col_form = detect_form_column(df)
    
    status_text.write(f"✅ HP URL列: **{col_url}**")
    status_text.write(f"✅ フォームURL列: **{col_form if col_form else '新規作成'}**")
    
    if col_form is None:
        col_form = 'フォームURL'
        df[col_form] = ''
    
    # Step 2: 無効なフォームURLをクリア
    status_text.write("📝 Step2: 無効なURLをチェック中...")
    invalid_count = 0
    for i, row in df.iterrows():
        val = str(row[col_form]).strip() if not pd.isna(row[col_form]) else ''
        if val and val != 'nan' and not is_valid_form_url(val):
            df.at[i, col_form] = ''
            invalid_count += 1
    status_text.write(f"   → {invalid_count}件クリア")
    
    # Step 3: 既存フォームURLの有効性チェック
    status_text.write("📝 Step3: 既存フォームURLの有効性チェック...")
    dead_count = 0
    existing_urls = [
        (i, str(row[col_form]).strip())
        for i, row in df.iterrows()
        if str(row[col_form]).strip() and str(row[col_form]).strip() != 'nan'
    ]
    
    if existing_urls:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_url_alive, url): (i, url) for i, url in existing_urls}
            for future in as_completed(futures):
                i, url = futures[future]
                alive = future.result()
                if not alive:
                    df.at[i, col_form] = ''
                    dead_count += 1
        status_text.write(f"   → {dead_count}件の無効URL（404等）を除去")
    
    # Step 4: 重複削除
    status_text.write("📝 Step4: 重複削除中...")
    seen_domains = set()
    drop_indices = []
    for i, row in df.iterrows():
        val = str(row[col_form]).strip() if not pd.isna(row[col_form]) else ''
        if not val or val == 'nan':
            continue
        domain = get_domain(val)
        if domain:
            if domain in seen_domains:
                drop_indices.append(i)
            else:
                seen_domains.add(domain)
    df = df.drop(index=drop_indices).reset_index(drop=True)
    status_text.write(f"   → {len(drop_indices)}件削除（残り {len(df)}件）")
    
    # Step 5: フォームURL収集
    status_text.write(f"📝 Step5: フォームURL自動抽出中（並列{MAX_WORKERS}）...")
    tasks = []
    for i, row in df.iterrows():
        site_url = str(row[col_url]).strip() if not pd.isna(row[col_url]) else ''
        form_url = str(row[col_form]).strip() if not pd.isna(row[col_form]) else ''
        if form_url == 'nan':
            form_url = ''
        tasks.append((i, site_url, form_url))
    
    done = 0
    total = len(tasks)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_row, t): t for t in tasks}
        for future in as_completed(futures):
            idx, contact_url = future.result()
            if contact_url and str(contact_url).strip() and is_valid_form_url(contact_url):
                df.at[idx, col_form] = contact_url
            done += 1
            progress_bar.progress(done / total)
    
    filled_total = df[col_form].apply(
        lambda x: bool(str(x).strip()) and str(x).strip() != 'nan'
    ).sum()
    
    status_text.write(f"✨ 完了: フォームURL抽出 **{filled_total}/{len(df)}件** ({filled_total/len(df)*100:.1f}%)")
    
    return df, col_form


# ============================================================
# Streamlit UI
# ============================================================

st.divider()

# サイドバー
with st.sidebar:
    st.header("📋 使い方")
    st.markdown("""
    1. CSVファイルをアップロード
    2. 「処理開始」ボタンをクリック
    3. 抽出完了後、ダウンロード
    
    **必須:** HP URLが含まれた列が必要です
    """)
    
    st.header("⚙️ 設定")
    max_workers_slider = st.slider(
        "並列処理数",
        min_value=1,
        max_value=10,
        value=MAX_WORKERS,
        help="大きいほど速いが、サーバーに負荷がかかります"
    )

# メインエリア
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 CSVファイル選択")
    uploaded_file = st.file_uploader(
        "CSVファイルをアップロード",
        type=["csv"],
        help="HP URLを含むCSVファイルを選択してください"
    )

with col2:
    st.subheader("📊 ファイル情報")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        st.write(f"**行数**: {len(df)}")
        st.write(f"**列数**: {len(df.columns)}")
        st.write("**列一覧**:")
        for i, col in enumerate(df.columns, 1):
            st.write(f"  {i}. {col}")

st.divider()

# 処理実行
if uploaded_file is not None:
    if st.button("🚀 処理開始", use_container_width=True, type="primary"):
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        
        # プログレス表示
        progress_bar = st.progress(0)
        status_container = st.container()
        
        with status_container:
            # 処理実行
            df_result, col_form = process_csv(df, progress_bar, st)
            
            st.success("✅ 処理完了！")
            
            # 結果表示
            st.subheader("📊 処理結果")
            st.dataframe(df_result, use_container_width=True)
            
            # ダウンロード
            st.subheader("💾 ダウンロード")
            
            # CSV
            csv = df_result.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV ダウンロード",
                data=csv,
                file_name="contact_form_urls_完了.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # 統計情報
            st.subheader("📈 統計")
            filled = df_result[col_form].apply(
                lambda x: bool(str(x).strip()) and str(x).strip() != 'nan'
            ).sum()
            st.metric("フォームURL取得率", f"{filled}/{len(df_result)}", f"{filled/len(df_result)*100:.1f}%")

else:
    st.info("📤 まずはCSVファイルをアップロードしてください")

st.divider()

# フッター
st.markdown("""
---
**💡 Tips:**
- 処理時間はサイト数によって異なります（通常 30秒～2分）
- Streamlit Shareは無料で24時間実行可能です
- GitHub にコード管理することで、いつでも更新できます

**🔗 GitHub リポジトリ:** 
- このコードを GitHub にコミットして、Streamlit Share でデプロイしてください
""")
