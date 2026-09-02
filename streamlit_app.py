"""
問い合わせフォームURL抽出 - Streamlit版（シンプル版）
"""

import streamlit as st
import pandas as pd
import re
import random
import warnings
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

warnings.filterwarnings('ignore')

# ページ設定
st.set_page_config(
    page_title="フォームURL抽出ツール",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 問い合わせフォームURL自動抽出")
st.markdown("営業リストのHP URLから、問い合わせフォームURLを自動抽出・検証するクラウドツール")

# ============================================================
# 設定
# ============================================================
MAX_WORKERS = 5
TIMEOUT = 10

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
]

CONTACT_KEYWORDS = [
    'お問い合わせ', 'お問合わせ', '問い合わせ', '問合わせ',
    'contact', 'inquiry', 'form', 'フォーム'
]

EXTERNAL_FORM_DOMAINS = [
    'form.run', 'formrun.com', 'docs.google.com', 'forms.gle',
    'tayori.com', 'mailform.jp', 'formzu.net'
]

# ============================================================
# ユーティリティ関数
# ============================================================

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    }

def get_domain(url):
    if not url or pd.isna(url):
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        return urlparse(url).netloc.lower().removeprefix('www.')
    except:
        return None

def is_valid_form_url(url):
    if not url or pd.isna(url):
        return False
    url = str(url).strip()
    return url.startswith(('http://', 'https://'))

def find_contact_url(site_url):
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
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            if any(ord(c) > 127 for c in href):
                continue
            
            if any(kw.lower() in text for kw in CONTACT_KEYWORDS):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
            
            if any(domain in href for domain in EXTERNAL_FORM_DOMAINS):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
            
            if any(pattern in href.lower() for pattern in ['/contact', '/inquiry', '/form', '/toiawase']):
                contact_url = urljoin(site_url, href)
                if is_valid_form_url(contact_url):
                    return contact_url
        
        return None
    except:
        return None

def check_url_alive(url):
    try:
        resp = requests.head(url, headers=get_headers(), timeout=5, allow_redirects=True)
        return resp.status_code < 400
    except:
        try:
            resp = requests.get(url, headers=get_headers(), timeout=5, allow_redirects=True)
            return resp.status_code < 400
        except:
            return False

def detect_url_column(df):
    keywords = ['url', 'URL', 'ホームページ', 'hp', 'HP', 'サイト', 'web', 'Web']
    cols = list(df.columns)
    
    for c in cols:
        if any(k.lower() in str(c).lower() for k in keywords):
            return c
    
    return cols[0]

# ============================================================
# UI
# ============================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 CSVファイル選択")
    uploaded_file = st.file_uploader("CSVファイルをアップロード", type=["csv"])

with col2:
    st.subheader("📊 ファイル情報")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.write(f"**行数**: {len(df)}")
            st.write(f"**列数**: {len(df.columns)}")
            st.write("**列一覧**: " + ", ".join(df.columns))
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {str(e)}")

st.divider()

if uploaded_file is not None:
    if st.button("🚀 処理開始", use_container_width=True, type="primary"):
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            col_url = detect_url_column(df)
            status_text.write(f"✅ HP URL列: **{col_url}**")
            
            df['フォームURL'] = ''
            
            # フォームURL収集
            tasks = []
            for i, row in df.iterrows():
                site_url = str(row[col_url]).strip() if not pd.isna(row[col_url]) else ''
                tasks.append((i, site_url))
            
            done = 0
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(find_contact_url, url): (i, url) for i, url in tasks}
                for future in as_completed(futures):
                    i, url = futures[future]
                    contact_url = future.result()
                    if contact_url and is_valid_form_url(contact_url):
                        df.at[i, 'フォームURL'] = contact_url
                    done += 1
                    progress_bar.progress(done / len(tasks))
            
            # 結果表示
            st.success("✅ 処理完了！")
            st.subheader("📊 処理結果")
            st.dataframe(df, use_container_width=True)
            
            # ダウンロード
            st.subheader("💾 ダウンロード")
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV ダウンロード",
                data=csv,
                file_name="contact_form_urls_完了.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # 統計
            filled = (df['フォームURL'] != '').sum()
            st.metric("フォームURL取得率", f"{filled}/{len(df)}", f"{filled/len(df)*100:.1f}%")
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

else:
    st.info("📤 まずはCSVファイルをアップロードしてください")

st.divider()
st.markdown("💡 クラウド上で24時間実行可能。GitHub で管理できます。")
