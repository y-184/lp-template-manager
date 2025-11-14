#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LP Template Manager - HTML直接入力対応版
ChatGPTが生成したHTML+CSSをそのまま貼り付けて使える
"""

import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import html

# ページ設定
st.set_page_config(
    page_title="LP Template Manager - HTML Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS：シンプルで安全なスタイル
st.markdown("""
<style>
    /* 基本スタイル */
    .main {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    /* 入力項目のラベルを見やすく */
    label, .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* タイトル */
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 700;
    }
    
    /* ボタン */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* カード */
    .template-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .template-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* 成功・警告メッセージ */
    .stSuccess, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* コードエディタエリア */
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ===== セキュリティ関数 =====
def sanitize_html_basic(text: str) -> str:
    """基本的なHTMLエスケープ（テキスト表示用）"""
    if not text:
        return ""
    return html.escape(str(text))

def sanitize_user_html(html_content: str) -> str:
    """
    ユーザー入力HTMLのサニタイズ（XSS対策）
    - <script>タグの除去
    - on*属性の除去（onclick, onload等）
    - javascript:プロトコルの除去
    """
    if not html_content:
        return ""
    
    # <script>タグの除去
    sanitized = re.sub(
        r'<script[^>]*>.*?</script>', 
        '', 
        html_content, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # on*属性の除去
    sanitized = re.sub(
        r'\s+on\w+\s*=\s*["\'][^"\']*["\']', 
        '', 
        sanitized, 
        flags=re.IGNORECASE
    )
    
    # javascript:プロトコルの除去
    sanitized = re.sub(
        r'href\s*=\s*["\']javascript:[^"\']*["\']', 
        'href="#"', 
        sanitized, 
        flags=re.IGNORECASE
    )
    
    return sanitized

def check_html_size(html_content: str, max_size_mb: float = 1.0) -> tuple[bool, str]:
    """
    HTMLサイズチェック
    Returns: (is_valid, error_message)
    """
    size_bytes = len(html_content.encode('utf-8'))
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb > max_size_mb:
        return False, f"HTMLサイズが大きすぎます: {size_mb:.2f}MB (上限: {max_size_mb}MB)"
    
    return True, ""

def check_base64_images(html_content: str) -> tuple[bool, str]:
    """
    base64埋め込み画像のチェック
    Returns: (is_valid, warning_message)
    """
    base64_pattern = r'data:image/[^;]+;base64,'
    matches = re.findall(base64_pattern, html_content, re.IGNORECASE)
    
    if matches:
        return False, f"⚠️ base64埋め込み画像が{len(matches)}個検出されました。URL参照に変更してください。"
    
    return True, ""

def validate_html_structure(html_content: str) -> tuple[bool, str]:
    """
    HTML構造の基本的な検証
    Returns: (is_valid, error_message)
    """
    # DOCTYPE or <html>タグの存在チェック
    if not (re.search(r'<!DOCTYPE\s+html', html_content, re.IGNORECASE) or 
            re.search(r'<html', html_content, re.IGNORECASE)):
        return False, "❌ 有効なHTML構造ではありません。<!DOCTYPE html>または<html>タグが必要です。"
    
    return True, ""

# ===== セッション状態の初期化 =====
if 'templates' not in st.session_state:
    st.session_state.templates = []

if 'drafts' not in st.session_state:
    st.session_state.drafts = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'template'

# ===== テンプレート管理関数 =====
def save_template(template_data: Dict):
    """テンプレートを保存"""
    template_data['created_at'] = datetime.now().isoformat()
    template_data['id'] = len(st.session_state.templates) + 1
    st.session_state.templates.append(template_data)

def save_draft(draft_data: Dict):
    """下書きを保存"""
    draft_data['saved_at'] = datetime.now().isoformat()
    draft_data['id'] = len(st.session_state.drafts) + 1
    st.session_state.drafts.append(draft_data)

def export_templates() -> str:
    """全テンプレートをJSON文字列としてエクスポート"""
    export_data = {
        'templates': st.session_state.templates,
        'drafts': st.session_state.drafts,
        'exported_at': datetime.now().isoformat()
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def import_templates(json_str: str) -> bool:
    """JSON文字列からテンプレートをインポート"""
    try:
        data = json.loads(json_str)
        if 'templates' in data:
            st.session_state.templates = data['templates']
        if 'drafts' in data:
            st.session_state.drafts = data['drafts']
        return True
    except Exception as e:
        st.error(f"インポートエラー: {str(e)}")
        return False

# ===== サイドバー =====
with st.sidebar:
    st.title("🎨 LP Template Manager")
    st.markdown("### HTML Edition")
    st.markdown("---")
    
    mode = st.radio(
        "モード選択",
        options=['template', 'design'],
        format_func=lambda x: "📝 テンプレート登録" if x == 'template' else "🎨 デザイン作成"
    )
    st.session_state.current_mode = mode
    
    st.markdown("---")
    st.markdown("### 📊 統計")
    st.metric("登録テンプレート", len(st.session_state.templates))
    st.metric("下書き", len(st.session_state.drafts))
    
    # テンプレート形式の内訳
    html_count = sum(1 for t in st.session_state.templates if t.get('template_type') == 'html')
    json_count = sum(1 for t in st.session_state.templates if t.get('template_type') == 'json')
    st.caption(f"HTML形式: {html_count} / JSON形式: {json_count}")
    
    st.markdown("---")
    st.markdown("### 💾 データ管理")
    
    # エクスポート
    if st.button("📤 全データをエクスポート"):
        export_json = export_templates()
        st.download_button(
            label="💾 JSONをダウンロード",
            data=export_json,
            file_name=f"lp_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # インポート
    uploaded_file = st.file_uploader("📥 JSONをインポート", type=['json'])
    if uploaded_file:
        json_str = uploaded_file.read().decode('utf-8')
        if st.button("インポート実行"):
            if import_templates(json_str):
                st.success("✅ インポート成功！")
                st.rerun()

# ===== メインコンテンツ =====
if st.session_state.current_mode == 'template':
    st.title("📝 テンプレート登録モード")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Step 1: 事例収集",
        "🤖 Step 2: プロンプト生成",
        "👀 Step 3: プレビュー",
        "💾 Step 4: 保存"
    ])
    
    # Step 1: 事例収集
    with tab1:
        st.header("📋 LP事例の情報を入力")
        
        col1, col2 = st.columns(2)
        with col1:
            template_name = st.text_input("テンプレート名", placeholder="例: freee会計 ヒーローセクション")
            category = st.selectbox("カテゴリ", [
                "BtoB SaaS",
                "EC/通販",
                "教育",
                "金融",
                "医療",
                "その他"
            ])
        
        with col2:
            source_url = st.text_input("元サイトURL", placeholder="https://...")
            industry = st.text_input("業種", placeholder="例: 会計ソフト")
        
        st.markdown("---")
        
        # ★新機能：テンプレート形式の選択
        st.subheader("📝 テンプレート形式")
        template_type = st.radio(
            "出力形式を選択",
            options=['html', 'json'],
            format_func=lambda x: "🌐 HTML形式（推奨）- ChatGPTが生成したHTMLをそのまま貼り付け" if x == 'html' 
                                  else "📊 JSON形式（旧方式）- 構造化データで管理",
            horizontal=True
        )
        
        st.info(f"""
        **{'HTML形式' if template_type == 'html' else 'JSON形式'}を選択しました**
        
        {'✅ どんな複雑なデザインでも再現可能' if template_type == 'html' else '⚠️ 構造が複雑な場合は表現に限界があります'}
        {'✅ ChatGPTが生成したコードをそのまま使える' if template_type == 'html' else '✅ データとして管理しやすい'}
        {'✅ メンテナンス不要（構造変更に対応不要）' if template_type == 'html' else '⚠️ 新しい構造には関数の拡張が必要'}
        """)
        
        # セクション選択（JSON形式の場合のみ）
        if template_type == 'json':
            section_type = st.selectbox("セクションタイプ", [
                "hero",
                "features",
                "testimonials",
                "how_it_works",
                "pricing",
                "faq",
                "cta",
                "social_proof",
                "comparison",
                "demo"
            ])
        else:
            section_type = None
        
        # 簡易メモ
        notes = st.text_area(
            "デザインメモ",
            placeholder="このLPの特徴やポイントを自由に記述...\n例: 青いCTAカードが2つ横並び、左右分割レイアウト、淡い青のグラデーション背景",
            height=150
        )
        
        if st.button("✅ Step 2へ進む", type="primary"):
            st.session_state.step1_data = {
                'name': template_name,
                'category': category,
                'source_url': source_url,
                'industry': industry,
                'template_type': template_type,
                'section_type': section_type,
                'notes': notes
            }
            st.success("✅ 情報を保存しました！Step 2へお進みください。")
    
    # Step 2: プロンプト生成
    with tab2:
        st.header("🤖 ChatGPT用プロンプトを生成")
        
        if 'step1_data' not in st.session_state:
            st.warning("⚠️ まずStep 1で基本情報を入力してください。")
        else:
            data = st.session_state.step1_data
            
            st.info(f"""
            **テンプレート名**: {data['name']}  
            **カテゴリ**: {data['category']}  
            **形式**: {data['template_type'].upper()}
            {f"**セクション**: {data['section_type']}" if data['section_type'] else ""}
            """)
            
            # プロンプト生成（HTML形式 or JSON形式）
            if data['template_type'] == 'html':
                # HTML形式のプロンプト
                prompt = f"""以下のLP事例を分析し、完全なHTML+CSSコードを生成してください。

【基本情報】
- テンプレート名: {data['name']}
- カテゴリ: {data['category']}
- 業種: {data['industry']}
- 元サイトURL: {data['source_url']}

【デザインメモ】
{data['notes']}

【重要な要件】
1. <!DOCTYPE html>から</html>までの完全なコード
2. Tailwind CDN または インラインCSSを使用
3. レスポンシブ対応（max-width: 1200px推奨）
4. 画像はURL参照のみ（src="https://..."）
   ❌ base64埋め込みは禁止
5. <script>タグは使用しない（純粋なHTML+CSSのみ）
6. フォントはGoogle Fonts CDN使用可
7. 元サイトのデザインを可能な限り忠実に再現

【出力形式】
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- 必要に応じてGoogle Fontsなど -->
    <style>
        /* カスタムスタイル */
    </style>
</head>
<body>
    <!-- 実際のコンテンツ -->
    <section>
        <!-- ヒーローセクション、機能紹介など -->
    </section>
</body>
</html>
```

【注意事項】
- 色、フォントサイズ、余白など、細部まで元サイトに近づけてください
- ホバー効果、影、グラデーションなども忠実に再現
- 画像はプレースホルダーテキストまたは https://via.placeholder.com/ を使用
"""
            else:
                # JSON形式のプロンプト（旧方式）
                prompt = f"""以下のLP事例を分析し、JSON形式でテンプレートを作成してください。

【基本情報】
- テンプレート名: {data['name']}
- カテゴリ: {data['category']}
- 業種: {data['industry']}
- 元サイトURL: {data['source_url']}
- セクションタイプ: {data['section_type']}

【デザインメモ】
{data['notes']}

【出力形式】
```json
{{
  "name": "{data['name']}",
  "category": "{data['category']}",
  "sections": [
    {{
      "type": "{data['section_type']}",
      "content": {{ /* コンテンツの詳細構造 */ }},
      "layout": {{ /* レイアウト設定 */ }},
      "background": {{ /* 背景設定 */ }}
    }}
  ]
}}
```
"""
            
            st.markdown("### 📋 生成されたプロンプト")
            st.code(prompt, language="text")
            
            if st.button("📋 プロンプトをコピー"):
                st.session_state.generated_prompt = prompt
                st.success("✅ プロンプトをコピーしました！ChatGPTに貼り付けて出力を取得してください。")
            
            st.markdown("---")
            
            # 入力エリア（HTML or JSON）
            if data['template_type'] == 'html':
                st.markdown("### 📥 ChatGPTからのHTML出力を貼り付け")
                
                html_input = st.text_area(
                    "HTML+CSSコード",
                    placeholder='<!DOCTYPE html>\n<html lang="ja">\n<head>...',
                    height=400,
                    help="ChatGPTが生成した完全なHTMLコードをそのまま貼り付けてください"
                )
                
                if st.button("✅ HTMLを検証してStep 3へ", type="primary"):
                    # サイズチェック
                    is_valid_size, size_error = check_html_size(html_input)
                    if not is_valid_size:
                        st.error(size_error)
                    else:
                        # base64画像チェック
                        is_no_base64, base64_warning = check_base64_images(html_input)
                        if not is_no_base64:
                            st.warning(base64_warning)
                        
                        # HTML構造チェック
                        is_valid_html, html_error = validate_html_structure(html_input)
                        if not is_valid_html:
                            st.error(html_error)
                        else:
                            # サニタイズ
                            sanitized = sanitize_user_html(html_input)
                            
                            st.session_state.step2_html = {
                                'original': html_input,
                                'sanitized': sanitized,
                                'type': 'html'
                            }
                            st.success("✅ HTML検証成功！Step 3でプレビューを確認できます。")
                            
                            if not is_no_base64:
                                st.warning("⚠️ base64画像が検出されましたが、検証は通過しました。可能であればURL参照に変更してください。")
            
            else:
                # JSON入力（旧方式）
                st.markdown("### 📥 ChatGPTからのJSON出力を貼り付け")
                
                json_input = st.text_area(
                    "JSON出力",
                    placeholder='{"name": "...", "category": "...", "sections": [...]}',
                    height=300
                )
                
                if st.button("✅ JSONを検証してStep 3へ", type="primary"):
                    try:
                        parsed_json = json.loads(json_input)
                        st.session_state.step2_html = {
                            'data': parsed_json,
                            'type': 'json'
                        }
                        st.success("✅ JSON検証成功！Step 3でプレビューを確認できます。")
                    except json.JSONDecodeError as e:
                        st.error(f"❌ JSON解析エラー: {str(e)}")
    
    # Step 3: プレビュー
    with tab3:
        st.header("👀 プレビュー確認")
        
        if 'step2_html' not in st.session_state:
            st.warning("⚠️ まずStep 2でHTML/JSONを入力・検証してください。")
        else:
            template_data = st.session_state.step2_html
            
            if template_data['type'] == 'html':
                # HTML形式のプレビュー
                st.info("**HTML形式のテンプレート**")
                
                st.markdown("### 🔍 プレビュー")
                
                # HTMLダウンロードボタン
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.download_button(
                        label="💾 HTMLをダウンロード",
                        data=template_data['original'],
                        file_name=f"{st.session_state.step1_data.get('name', 'template')}.html",
                        mime="text/html"
                    )
                
                # iframe内にプレビュー表示（完全隔離）
                st.components.v1.html(
                    template_data['sanitized'],
                    height=800,
                    scrolling=True
                )
                
                st.success("✅ プレビューが表示されました。問題なければStep 4で保存してください。")
                
                # サニタイズ情報の表示
                with st.expander("🔒 セキュリティ情報"):
                    st.write("**適用されたサニタイズ処理:**")
                    st.write("- `<script>`タグの除去")
                    st.write("- `on*`属性（onclick等）の除去")
                    st.write("- `javascript:`プロトコルの除去")
                    st.write("- iframe内に隔離表示（CSS汚染防止）")
            
            else:
                # JSON形式のプレビュー（旧方式）
                st.info("**JSON形式のテンプレート**")
                st.warning("⚠️ JSON形式のプレビュー生成は現在未対応です。HTML形式の使用を推奨します。")
                st.json(template_data['data'])
    
    # Step 4: 保存
    with tab4:
        st.header("💾 テンプレートを保存")
        
        if 'step2_html' not in st.session_state or 'step1_data' not in st.session_state:
            st.warning("⚠️ まずStep 1-3を完了してください。")
        else:
            step1 = st.session_state.step1_data
            step2 = st.session_state.step2_html
            
            # 保存データの作成
            save_data = {
                'name': step1['name'],
                'category': step1['category'],
                'source_url': step1['source_url'],
                'industry': step1['industry'],
                'template_type': step1['template_type'],
                'notes': step1['notes']
            }
            
            if step2['type'] == 'html':
                save_data['html_content'] = step2['original']
                save_data['html_sanitized'] = step2['sanitized']
            else:
                save_data['json_data'] = step2['data']
                save_data['section_type'] = step1.get('section_type')
            
            # プレビュー
            st.subheader("📋 保存内容の確認")
            st.write(f"**テンプレート名**: {save_data['name']}")
            st.write(f"**カテゴリ**: {save_data['category']}")
            st.write(f"**形式**: {save_data['template_type'].upper()}")
            st.write(f"**元サイト**: {save_data['source_url']}")
            
            if save_data['template_type'] == 'html':
                html_size = len(save_data['html_content'].encode('utf-8')) / 1024
                st.write(f"**HTMLサイズ**: {html_size:.2f} KB")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 下書きとして保存", use_container_width=True):
                    save_draft(save_data.copy())
                    st.success("✅ 下書きを保存しました！")
            
            with col2:
                if st.button("✅ 承認して本登録", type="primary", use_container_width=True):
                    save_template(save_data.copy())
                    st.success("🎉 テンプレートを本登録しました！")
                    st.balloons()
                    
                    # クリーンアップ
                    if 'step1_data' in st.session_state:
                        del st.session_state.step1_data
                    if 'step2_html' in st.session_state:
                        del st.session_state.step2_html
                    
                    st.info("💡 新しいテンプレートを登録する場合は、Step 1から再度入力してください。")
    
    # 保存済みテンプレート一覧
    st.markdown("---")
    st.header("📚 保存済みテンプレート一覧")
    
    if not st.session_state.templates:
        st.info("まだテンプレートが登録されていません。")
    else:
        for template in st.session_state.templates:
            template_type = template.get('template_type', 'unknown')
            type_badge = "🌐 HTML" if template_type == 'html' else "📊 JSON"
            
            with st.expander(f"{type_badge} {template.get('name', 'Unnamed')} ({template.get('category', 'N/A')})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**作成日**: {template.get('created_at', 'N/A')[:10]}")
                    st.write(f"**業種**: {template.get('industry', 'N/A')}")
                    if template.get('source_url'):
                        st.write(f"**元サイト**: {template['source_url']}")
                
                with col2:
                    if template_type == 'html':
                        html_size = len(template.get('html_content', '').encode('utf-8')) / 1024
                        st.metric("HTMLサイズ", f"{html_size:.1f} KB")
                    
                    if template.get('notes'):
                        with st.expander("📝 メモを表示"):
                            st.write(template['notes'])
                
                with col3:
                    if st.button("🗑️ 削除", key=f"del_{template['id']}"):
                        st.session_state.templates.remove(template)
                        st.rerun()
                
                # プレビュー・ダウンロード
                if template_type == 'html':
                    st.download_button(
                        label="💾 HTMLをダウンロード",
                        data=template.get('html_content', ''),
                        file_name=f"{template.get('name', 'template')}.html",
                        mime="text/html",
                        key=f"download_{template['id']}"
                    )
                    
                    if st.button("👀 プレビューを表示", key=f"preview_{template['id']}"):
                        st.components.v1.html(
                            template.get('html_sanitized', template.get('html_content', '')),
                            height=600,
                            scrolling=True
                        )

else:
    # デザイン作成モード
    st.title("🎨 デザイン作成モード")
    st.info("🚧 デザイン作成モードは開発中です。テンプレート登録モードをご利用ください。")

# フッター
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6B7280; font-size: 14px; padding: 2rem 0;">
    <p><strong>LP Template Manager - HTML Edition</strong></p>
    <p>ChatGPTが生成したHTML+CSSをそのまま使える 🚀</p>
    <p style="font-size: 12px; margin-top: 1rem;">
        登録済み: HTML形式 {sum(1 for t in st.session_state.templates if t.get('template_type') == 'html')}件 / 
        JSON形式 {sum(1 for t in st.session_state.templates if t.get('template_type') == 'json')}件
    </p>
</div>
""", unsafe_allow_html=True)
