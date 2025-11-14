import streamlit as st
import json
import re
import html
from datetime import datetime
import uuid

# ページ設定
st.set_page_config(
    page_title="LP Template Manager - Final",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== スタイル定義 =====

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #F9FAFB; }
    
    /* タブスタイル改善 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F3F4F6;
        padding: 8px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 6px;
        padding: 0 24px;
        font-weight: 600;
        font-size: 15px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* プロンプトボックス */
    .prompt-box {
        background: #F9FAFB;
        border: 2px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* コピーボタン */
    .copy-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .copy-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* バックアップアラート */
    .backup-alert {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
    }
    
    .backup-alert h3 {
        color: #fff !important;
        margin-bottom: 10px;
        font-size: 20px;
    }
    
    /* ヘルプボックス */
    .help-box {
        background: #EEF2FF;
        border-left: 4px solid #667eea;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== ChatGPT連携プロンプトテンプレート =====

SECTION_PROMPTS = {
    "hero": """以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {template_name}
- セクション種別: hero（ヒーローセクション）
- 参照URL: {reference_url}
- 説明: {description}

【セクションの特徴】
heroセクションは、LPのファーストビューを担う最重要セクションです。
- メインメッセージで価値を即座に伝える
- ビジュアルで感情に訴える
- CTAで次のアクションを明確化

【出力すべきJSON項目】
```json
{{
  "main_headline": "メインヘッドライン（20-40文字、顧客の得られる価値を明確に）",
  "sub_headline": "サブヘッドライン（より具体的な説明、40-80文字）",
  "description": "詳細説明（100-200文字、具体的なベネフィット）",
  "cta_primary": "主要CTAボタンテキスト（例: 無料で始める）",
  "cta_secondary": "副次CTAボタンテキスト（例: 資料請求）",
  "hero_image_description": "ヒーロー画像の説明（プロダクト画面、利用シーン等）",
  "trust_elements": ["信頼要素1（例: 導入社数10,000社）", "信頼要素2（例: 満足度98%）"],
  "background_style": "背景スタイル（gradient/solid/image等）",
  "layout_type": "レイアウトタイプ（center/left-right/split等）"
}}
```

【BtoB SaaS特化の観点】
- 「誰のどんな課題を解決するか」を明確に
- 数値やデータで信頼性を担保
- 無料トライアル/デモ申込みへの導線を重視
- 企業ロゴや導入実績で権威性を演出

【注意事項】
- 著作権に配慮し、コピーは抽象化・一般化してください
- 構造とレイアウトのパターンのみを抽出してください
- 固有名詞は汎用的な表現に置き換えてください

上記JSON形式で出力してください。
""",
    
    "features": """以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {template_name}
- セクション種別: features（機能紹介）
- 参照URL: {reference_url}
- 説明: {description}

【出力すべきJSON項目】
```json
{{
  "section_title": "セクションタイトル（例: 主要機能）",
  "introduction": "導入文（機能の全体像を説明）",
  "features": [
    {{
      "title": "機能1のタイトル",
      "description": "機能1の詳細説明",
      "icon": "アイコン（例: ⚡）",
      "benefit": "この機能で得られるベネフィット"
    }},
    {{
      "title": "機能2のタイトル",
      "description": "機能2の詳細説明",
      "icon": "アイコン（例: 🎯）",
      "benefit": "この機能で得られるベネフィット"
    }}
  ],
  "layout_type": "レイアウトタイプ（grid/list等）"
}}
```

上記JSON形式で出力してください。
""",
    
    "testimonials": """以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {template_name}
- セクション種別: testimonials（お客様の声）
- 参照URL: {reference_url}
- 説明: {description}

【出力すべきJSON項目】
```json
{{
  "section_title": "セクションタイトル（例: お客様の声）",
  "testimonials": [
    {{
      "quote": "お客様のコメント",
      "author": "氏名",
      "company": "企業名",
      "position": "役職",
      "avatar_description": "アバター画像の説明（オプション）"
    }}
  ]
}}
```

上記JSON形式で出力してください。
""",
    
    "social_proof": """以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {template_name}
- セクション種別: social_proof（導入企業）
- 参照URL: {reference_url}
- 説明: {description}

【出力すべきJSON項目】
```json
{{
  "section_title": "セクションタイトル（例: 導入企業）",
  "companies": ["企業名1", "企業名2", "企業名3"],
  "stats": {{
    "total_companies": "導入企業数",
    "satisfaction_rate": "満足度",
    "active_users": "アクティブユーザー数"
  }}
}}
```

上記JSON形式で出力してください。
""",
    
    "faq": """以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {template_name}
- セクション種別: faq（よくある質問）
- 参照URL: {reference_url}
- 説明: {description}

【出力すべきJSON項目】
```json
{{
  "section_title": "セクションタイトル（例: よくある質問）",
  "questions": [
    {{
      "question": "質問1",
      "answer": "回答1"
    }},
    {{
      "question": "質問2",
      "answer": "回答2"
    }}
  ]
}}
```

上記JSON形式で出力してください。
"""
}

SECTION_LABELS = {
    "hero": "ヒーローセクション（ファーストビュー）",
    "header": "シンプルヘッダー",
    "trouble": "お悩み・課題提示",
    "features": "機能紹介",
    "how_it_works": "利用の流れ",
    "testimonials": "お客様の声",
    "social_proof": "導入企業・実績",
    "pricing": "料金表",
    "cta": "CTA・申し込みボタン",
    "faq": "よくある質問"
}

# ===== スマートバックアップ機能 =====

def show_smart_backup_alert(template_data):
    """新規テンプレート作成時のスマートバックアップアラート"""
    if not st.session_state.get('show_backup_alerts', True):
        return
    
    template_name = template_data.get('name', '新規テンプレート')
    
    alert_html = f"""
    <div class="backup-alert">
        <h3>🎉 テンプレート「{html.escape(template_name)}」を保存しました！</h3>
        <p style="margin-bottom: 15px;">💡 <strong>今すぐバックアップしませんか？</strong> 
        データが消失する前に、1クリックで安全に保存できます。</p>
        
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button onclick="copyToClipboard()" id="copyBtn" class="copy-button">
                📋 クリップボードにコピー
            </button>
            <button onclick="downloadTemplate()" id="downloadBtn" class="copy-button">
                💾 ファイルでダウンロード
            </button>
        </div>
    </div>
    
    <script>
    function copyToClipboard() {{
        const templateData = {json.dumps(template_data, ensure_ascii=False)};
        const jsonString = JSON.stringify(templateData, null, 2);
        
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(jsonString).then(function() {{
                document.getElementById('copyBtn').innerHTML = '✅ コピー完了！';
                setTimeout(() => {{
                    document.getElementById('copyBtn').innerHTML = '📋 クリップボードにコピー';
                }}, 2000);
            }});
        }}
    }}
    
    function downloadTemplate() {{
        const templateData = {json.dumps(template_data, ensure_ascii=False)};
        const jsonString = JSON.stringify(templateData, null, 2);
        const blob = new Blob([jsonString], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'template_{template_data.get('name', 'unnamed').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        document.getElementById('downloadBtn').innerHTML = '✅ ダウンロード完了！';
        setTimeout(() => {{
            document.getElementById('downloadBtn').innerHTML = '💾 ファイルでダウンロード';
        }}, 2000);
    }}
    </script>
    """
    
    st.markdown(alert_html, unsafe_allow_html=True)

def create_quick_backup_sidebar():
    """サイドバーのクイックバックアップ機能"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ クイックバックアップ")
    
    template_count = len(st.session_state.templates) if st.session_state.templates else 0
    
    if template_count > 0:
        st.sidebar.info(f"現在 **{template_count}個** のテンプレートを保存中")
        
        # 全体バックアップ
        backup_data = create_backup_data()
        if backup_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lp_templates_backup_{timestamp}.json"
            
            st.sidebar.download_button(
                label="💾 全テンプレートをダウンロード",
                data=backup_data,
                file_name=filename,
                mime="application/json",
                help="すべてのテンプレートをJSONファイルでダウンロード",
                use_container_width=True
            )
    else:
        st.sidebar.info("テンプレートがまだありません")
    
    # アラート設定
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 設定")
    
    show_alerts = st.sidebar.checkbox(
        "バックアップアラートを表示",
        value=st.session_state.get('show_backup_alerts', True),
        help="新規テンプレート作成時のアラート表示"
    )
    st.session_state.show_backup_alerts = show_alerts

def create_backup_data():
    """バックアップデータを作成"""
    if not st.session_state.templates:
        return None
    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'total_templates': len(st.session_state.templates),
        'templates': st.session_state.templates
    }
    
    return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')

# ===== ユーティリティ関数 =====

def init_session_state():
    """セッションステート初期化"""
    if 'templates' not in st.session_state:
        st.session_state.templates = {}
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "template_registration"
    if 'show_backup_alerts' not in st.session_state:
        st.session_state.show_backup_alerts = True

def save_template(template_data):
    """テンプレートを安全に保存"""
    try:
        if not isinstance(template_data, dict):
            st.error("❌ 無効なテンプレートデータです")
            return False
        
        if not template_data.get('name'):
            st.error("❌ テンプレート名が必要です")
            return False
        
        template_id = str(uuid.uuid4())
        template_data['id'] = template_id
        template_data['created_at'] = datetime.now().isoformat()
        
        st.session_state.templates[template_id] = template_data
        show_smart_backup_alert(template_data)
        
        return True
    
    except Exception as e:
        st.error(f"❌ 保存エラー: {str(e)}")
        return False

# ===== メインアプリケーション =====

def main():
    """メインアプリケーション"""
    init_session_state()
    
    st.title("📄 LP Template Manager")
    st.markdown("**BtoB SaaS特化のLPテンプレート管理ツール - 1クリックバックアップ・自動保存機能付き**")
    
    with st.sidebar:
        st.markdown("## 🎛️ 操作パネル")
        
        mode = st.radio(
            "モードを選択してください",
            ["template_registration", "design_creation"],
            format_func=lambda x: "📝 テンプレート登録" if x == "template_registration" else "🎨 デザイン作成",
            key="mode_selector"
        )
        
        st.session_state.current_mode = mode
        create_quick_backup_sidebar()
    
    if st.session_state.current_mode == "template_registration":
        show_template_registration_mode()
    else:
        show_design_creation_mode()

def show_template_registration_mode():
    """テンプレート登録モード（タブ切り替え式）"""
    
    st.markdown("""
    <div class="help-box">
        💡 <strong>使い方:</strong> 4つのステップでテンプレートを登録します<br>
        ① 基本情報入力 → ② プロンプト生成・ChatGPTへコピー → ③ JSONデータ入力 → ④ 保存
    </div>
    """, unsafe_allow_html=True)
    
    # タブ定義
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Step 1: 基本情報",
        "🤖 Step 2: プロンプト生成",
        "📋 Step 3: JSONデータ入力",
        "💾 Step 4: 保存・管理"
    ])
    
    # ===== Step 1: 基本情報 =====
    with tab1:
        st.markdown("### 📌 テンプレートの基本情報を入力")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### テンプレート名")
            st.caption("分かりやすい名前を付けてください（例: 「Slack風ヒーロー」）")
            template_name = st.text_input(
                "テンプレート名",
                placeholder="例: Slack風ヒーローセクション",
                key="template_name",
                label_visibility="collapsed"
            )
            
            st.markdown("#### 参考URL")
            st.caption("参考にしたLP事例のURL（任意）")
            reference_url = st.text_input(
                "参考URL",
                placeholder="https://example.com/landing-page",
                key="reference_url",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("#### セクション種別")
            st.caption("どの部分のテンプレートか選択してください")
            section_type = st.selectbox(
                "セクション種別",
                list(SECTION_LABELS.keys()),
                format_func=lambda x: SECTION_LABELS[x],
                key="section_type",
                label_visibility="collapsed"
            )
            
            st.markdown("#### 説明")
            st.caption("このテンプレートの特徴や使いどころ（任意）")
            description = st.text_area(
                "説明",
                placeholder="例: 大手SaaS企業風のシンプルで分かりやすいレイアウト",
                key="template_description",
                height=100,
                label_visibility="collapsed"
            )
        
        st.success("✅ 基本情報の入力が完了しました！次は「Step 2: プロンプト生成」タブに進んでください。")
    
    # ===== Step 2: プロンプト生成 =====
    with tab2:
        st.markdown("### 🤖 ChatGPTに投げるプロンプトを生成")
        
        st.markdown("""
        <div class="help-box">
            💡 <strong>このステップでやること:</strong><br>
            1. 下記の「プロンプトを生成」ボタンをクリック<br>
            2. 生成されたプロンプトを「コピー」ボタンでコピー<br>
            3. ChatGPTに貼り付けて、JSONデータを取得<br>
            4. 取得したJSONを「Step 3」で入力
        </div>
        """, unsafe_allow_html=True)
        
        # プロンプト生成ボタン
        if st.button("🚀 プロンプトを生成", key="generate_prompt", type="primary", use_container_width=True):
            template_name = st.session_state.get('template_name', 'サンプルテンプレート')
            section_type = st.session_state.get('section_type', 'hero')
            reference_url = st.session_state.get('reference_url', 'https://example.com')
            description = st.session_state.get('template_description', '説明なし')
            
            # プロンプトテンプレートから生成
            if section_type in SECTION_PROMPTS:
                prompt = SECTION_PROMPTS[section_type].format(
                    template_name=template_name,
                    reference_url=reference_url,
                    description=description
                )
                
                st.session_state.generated_prompt = prompt
            else:
                st.warning(f"⚠️ セクション「{section_type}」のプロンプトテンプレートがまだ用意されていません。")
        
        # 生成されたプロンプトを表示
        if 'generated_prompt' in st.session_state:
            st.markdown("### 📄 生成されたプロンプト")
            st.markdown(f'<div class="prompt-box">{html.escape(st.session_state.generated_prompt)}</div>', unsafe_allow_html=True)
            
            # コピーボタン
            copy_js = f"""
            <button onclick="copyPrompt()" id="copyPromptBtn" class="copy-button" style="margin-top: 12px;">
                📋 プロンプトをコピー
            </button>
            
            <script>
            function copyPrompt() {{
                const promptText = {json.dumps(st.session_state.generated_prompt)};
                
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(promptText).then(function() {{
                        document.getElementById('copyPromptBtn').innerHTML = '✅ コピーしました！ChatGPTに貼り付けてください';
                        setTimeout(() => {{
                            document.getElementById('copyPromptBtn').innerHTML = '📋 プロンプトをコピー';
                        }}, 3000);
                    }});
                }}
            }}
            </script>
            """
            st.markdown(copy_js, unsafe_allow_html=True)
            
            st.success("✅ プロンプトをコピーして、ChatGPTに貼り付けてください！取得したJSONを「Step 3」で入力します。")
    
    # ===== Step 3: JSONデータ入力 =====
    with tab3:
        st.markdown("### 📋 ChatGPTから取得したJSONデータを入力")
        
        st.markdown("""
        <div class="help-box">
            💡 <strong>このステップでやること:</strong><br>
            1. ChatGPTから取得したJSONデータをそのままコピー<br>
            2. 下記のテキストエリアに貼り付け<br>
            3. 「JSONをパース」ボタンでプレビュー確認
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### JSONデータ")
        st.caption("ChatGPTから取得したJSONデータをここに貼り付けてください")
        json_input = st.text_area(
            "JSONデータ",
            placeholder='''{
  "main_headline": "チームコミュニケーションを、もっと楽しく",
  "sub_headline": "Slackは、チームの生産性を向上させるコラボレーションツールです",
  "description": "メール、チャット、ファイル共有を1つに。",
  "cta_primary": "無料で始める",
  "trust_elements": ["導入企業数10,000社", "満足度98%"]
}''',
            height=250,
            key="json_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 JSONをパース", key="parse_json", use_container_width=True):
                try:
                    if json_input.strip():
                        parsed_data = json.loads(json_input)
                        
                        template_name = st.session_state.get('template_name', f"テンプレート_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        section_type = st.session_state.get('section_type', 'hero')
                        reference_url = st.session_state.get('reference_url', '')
                        description = st.session_state.get('template_description', '')
                        
                        template_data = {
                            'name': template_name,
                            'section_type': section_type,
                            'reference_url': reference_url,
                            'description': description,
                            'created_at': datetime.now().isoformat(),
                            **parsed_data
                        }
                        
                        st.session_state.temp_template = template_data
                        st.success("✅ JSONデータをパースしました！下記でプレビューを確認してください。")
                    else:
                        st.error("❌ JSONデータを入力してください")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON解析エラー: {str(e)}")
                    st.info("💡 ヒント: JSONの形式が正しいか確認してください")
                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")
        
        with col2:
            if st.button("🔄 入力をクリア", key="clear_json", use_container_width=True):
                st.session_state.json_input = ""
                st.rerun()
        
        # プレビュー表示
        if 'temp_template' in st.session_state:
            st.markdown("### 👀 プレビュー")
            st.json(st.session_state.temp_template)
            st.success("✅ パース成功！「Step 4: 保存・管理」タブで保存してください。")
    
    # ===== Step 4: 保存・管理 =====
    with tab4:
        st.markdown("### 💾 テンプレートの保存・管理")
        
        # 保存ボタン
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 テンプレート保存", key="save_template", type="primary", use_container_width=True):
                if 'temp_template' in st.session_state:
                    success = save_template(st.session_state.temp_template)
                    if success:
                        if 'temp_template' in st.session_state:
                            del st.session_state.temp_template
                        st.rerun()
                else:
                    st.error("❌ 先にStep 3でJSONをパースしてください")
        
        with col2:
            if st.button("🗑️ 作業をクリア", key="clear_all", use_container_width=True):
                keys_to_clear = ['template_name', 'reference_url', 'section_type', 'template_description', 
                                'json_input', 'temp_template', 'generated_prompt']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ 作業内容をクリアしました")
                st.rerun()
        
        # 保存済みテンプレート一覧
        if st.session_state.templates:
            st.markdown("---")
            st.markdown("### 📚 保存済みテンプレート一覧")
            
            for template_id, template in st.session_state.templates.items():
                with st.expander(f"📄 {template.get('name', '無名')} - {SECTION_LABELS.get(template.get('section_type', 'unknown'), '不明')}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**作成日時:** {template.get('created_at', 'N/A')[:19]}")
                        if template.get('description'):
                            st.write(f"**説明:** {template.get('description')}")
                        if template.get('reference_url'):
                            st.write(f"**参考URL:** {template.get('reference_url')}")
                    
                    with col2:
                        if st.button("🎨 編集", key=f"edit_{template_id}", use_container_width=True):
                            st.session_state.selected_template = template_id
                            st.session_state.current_mode = "design_creation"
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️ 削除", key=f"delete_{template_id}", use_container_width=True):
                            del st.session_state.templates[template_id]
                            st.success("✅ テンプレートを削除しました")
                            st.rerun()
                    
                    with st.expander("📄 JSONデータを表示"):
                        st.json(template)

def show_design_creation_mode():
    """デザイン作成モード"""
    st.markdown("### 🎨 デザイン作成モード")
    
    if not st.session_state.templates:
        st.warning("⚠️ テンプレートが登録されていません。")
        if st.button("📝 テンプレート登録モードへ移動"):
            st.session_state.current_mode = "template_registration"
            st.rerun()
        return
    
    st.info("💡 登録済みテンプレートを選択して編集できます（開発中）")

if __name__ == "__main__":
    main()
