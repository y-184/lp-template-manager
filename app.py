import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid

# ページ設定
st.set_page_config(
    page_title="LP Template Manager",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tailwind CSS読み込み
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    .stApp {
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# ===== セッションステート初期化 =====

def init_session_state():
    """セッションステートを初期化"""
    if "templates" not in st.session_state:
        # 初期データ読み込み
        template_file = Path("data/templates.json")
        if template_file.exists():
            with open(template_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.templates = data["templates"]
        else:
            # デフォルトサンプル
            st.session_state.templates = [
                {
                    "template_id": "sample_header_001",
                    "display_name": "BtoB SaaS向けクリーンヘッダー",
                    "section_type": "header",
                    "status": "approved",
                    "metadata": {
                        "source_url": "https://example.com",
                        "description": "シンプルで迷わないヘッダー構成。BtoB向け。",
                        "screenshot_url": "",
                        "tags": ["BtoB", "SaaS", "シンプル"],
                        "created_by": "ichihashi",
                        "created_at": "2025-01-13",
                        "updated_at": "2025-01-13",
                        "review_comment": ""
                    },
                    "layout": {
                        "alignment": "center",
                        "background_color": "#F8FAFC",
                        "image_url": ""
                    },
                    "content": {
                        "title": "革新的なマーケティングオートメーション",
                        "subtitle": "リード獲得から受注まで、業務効率を3倍に",
                        "bullets": [],
                        "cta_label": "無料で試してみる",
                        "price_table": [],
                        "form_fields": []
                    },
                    "notes": "サンプルテンプレート"
                }
            ]
    
    # 編集中テンプレートID
    if "editing_template_id" not in st.session_state:
        st.session_state.editing_template_id = None

# 初期化実行
init_session_state()

# ===== データ管理関数 =====

def get_templates():
    """テンプレートデータを取得"""
    return st.session_state.templates

def get_template_by_id(template_id):
    """IDでテンプレートを取得"""
    for template in st.session_state.templates:
        if template["template_id"] == template_id:
            return template
    return None

def add_template(template):
    """テンプレートを追加"""
    st.session_state.templates.append(template)

def update_template(template_id, updates):
    """テンプレートを更新"""
    for i, template in enumerate(st.session_state.templates):
        if template["template_id"] == template_id:
            st.session_state.templates[i].update(updates)
            st.session_state.templates[i]["metadata"]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
            break

def delete_template(template_id):
    """テンプレートを削除"""
    st.session_state.templates = [
        t for t in st.session_state.templates 
        if t["template_id"] != template_id
    ]

def export_templates_json():
    """JSON形式でエクスポート"""
    return json.dumps({"templates": st.session_state.templates}, ensure_ascii=False, indent=2)

# ===== プレビュー生成関数 =====

def generate_template_preview(template, brand_color="#2563EB"):
    """テンプレートのHTMLプレビューを生成"""
    bg_color = template['layout'].get('background_color', '#FFFFFF')
    alignment = template['layout'].get('alignment', 'center')
    
    html = f"""
    <div style="max-width: 1200px; margin: 0 auto; background: {bg_color}; padding: 60px 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: {alignment};">
    """
    
    # タイトル
    if template['content'].get('title'):
        html += f"""
        <h2 style="font-size: 2.5rem; font-weight: bold; color: #1F2937; margin-bottom: 16px;">
            {template['content']['title']}
        </h2>
        """
    
    # サブタイトル
    if template['content'].get('subtitle'):
        html += f"""
        <p style="font-size: 1.25rem; color: #6B7280; margin-bottom: 24px;">
            {template['content']['subtitle']}
        </p>
        """
    
    # 箇条書き（お悩みセクション用）
    if template['content'].get('bullets') and len(template['content']['bullets']) > 0:
        html += '<div style="text-align: left; max-width: 600px; margin: 0 auto 24px;">'
        for bullet in template['content']['bullets']:
            html += f"""
            <div style="display: flex; align-items: start; margin-bottom: 12px;">
                <span style="color: {brand_color}; margin-right: 12px; font-size: 1.5rem;">✓</span>
                <span style="color: #374151; font-size: 1.1rem;">{bullet}</span>
            </div>
            """
        html += '</div>'
    
    # CTAボタン
    if template['content'].get('cta_label'):
        html += f"""
        <button style="background: {brand_color}; color: white; padding: 14px 36px; border-radius: 8px; border: none; font-size: 1.1rem; font-weight: 600; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {template['content']['cta_label']}
        </button>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html

# ===== メインUI =====

def main():
    # タイトル
    st.markdown("""
    <div class="text-center py-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">📄 LP Template Manager</h1>
        <p class="text-xl text-gray-600">LPのための Keynote</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー：メニュー選択
    with st.sidebar:
        st.markdown("### 🎯 メニュー")
        menu = st.radio(
            "モードを選択",
            ["🏠 ホーム", "📝 テンプレート登録", "🎨 LP作成", "📚 テンプレート一覧", "💾 データ管理"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 統計")
        
        # テンプレート統計
        templates = get_templates()
        total = len(templates)
        approved = len([t for t in templates if t["status"] == "approved"])
        draft = len([t for t in templates if t["status"] == "draft"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("総テンプレ", total)
        with col2:
            st.metric("承認済み", approved)
        
        # データ永続化の注意
        st.markdown("---")
        st.info("💡 データはセッション内のみ保持されます。「データ管理」からエクスポート可能です。")
    
    # メイン画面
    if menu == "🏠 ホーム":
        show_home()
    elif menu == "📝 テンプレート登録":
        show_template_registration()
    elif menu == "🎨 LP作成":
        show_page_builder()
    elif menu == "📚 テンプレート一覧":
        show_template_list()
    elif menu == "💾 データ管理":
        show_data_management()

# ===== 各画面 =====

def show_home():
    """ホーム画面"""
    st.markdown("""
    ## 👋 ようこそ！
    
    **LP Template Manager** は、優れたLP事例を「テンプレート化」して蓄積し、
    ページを組み上げられるツールです。
    
    ### 🎯 使い方
    
    1. **📝 テンプレート登録**  
       良いLP事例を見つけたら、構造化してテンプレートとして保存
    
    2. **🎨 LP作成**  
       承認済みテンプレートを組み合わせて、LP全体を作成
    
    3. **📚 テンプレート一覧**  
       登録したテンプレートを確認・管理
    
    4. **💾 データ管理**  
       テンプレートデータのエクスポート・インポート
    
    ### 🚀 さっそく始めましょう！
    
    左のメニューから「テンプレート登録」を選んで、最初のテンプレートを作成してみてください。
    """)
    
    # サンプルプレビュー
    templates = get_templates()
    if templates:
        st.markdown("---")
        st.markdown("### 📋 登録済みテンプレート例")
        
        template = templates[0]
        
        st.markdown(f"""
        <div class="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-xl font-bold text-gray-800">{template['display_name']}</h3>
                    <p class="text-gray-600 mt-2">{template['metadata']['description']}</p>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                    {template['status']}
                </span>
            </div>
            <div class="flex gap-2">
                <span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">{template['section_type']}</span>
                {''.join([f'<span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{tag}</span>' for tag in template['metadata']['tags']])}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_template_registration():
    """テンプレート登録画面"""
    st.markdown("## 📝 テンプレート登録")
    st.markdown("良いLP事例を構造化してテンプレートとして保存します。")
    
    # タブで3ステップを分ける
    tab1, tab2, tab3 = st.tabs(["Step 1: 基本情報", "Step 2: プロンプト生成", "Step 3: JSON入力・プレビュー"])
    
    # Step 1: 基本情報入力
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 基本情報入力")
            
            display_name = st.text_input("テンプレート名", placeholder="例: BtoB SaaS向けクリーンヘッダー", key="reg_name")
            
            section_type = st.selectbox(
                "セクション種別",
                ["header", "trouble", "pricing", "cta", "form"],
                key="reg_section"
            )
            
            source_url = st.text_input("参照URL", placeholder="https://example.com/lp", key="reg_url")
            
            description = st.text_area(
                "一言メモ",
                placeholder="このテンプレートの特徴や使いどころを記載",
                height=100,
                key="reg_desc"
            )
            
            screenshot_url = st.text_input("参考画像URL（任意）", placeholder="https://...", key="reg_img")
            
            tags_input = st.text_input("タグ（カンマ区切り）", placeholder="BtoB, SaaS, シンプル", key="reg_tags")
            
            if st.button("💾 基本情報を保存", type="primary", use_container_width=True):
                if not display_name:
                    st.error("⚠️ テンプレート名を入力してください")
                else:
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                    
                    # セッションに保存
                    st.session_state.draft_template = {
                        "template_id": str(uuid.uuid4()),
                        "display_name": display_name,
                        "section_type": section_type,
                        "status": "draft",
                        "metadata": {
                            "source_url": source_url,
                            "description": description,
                            "screenshot_url": screenshot_url,
                            "tags": tags,
                            "created_by": "user",
                            "created_at": datetime.now().strftime("%Y-%m-%d"),
                            "updated_at": datetime.now().strftime("%Y-%m-%d"),
                            "review_comment": ""
                        },
                        "layout": {
                            "alignment": "center",
                            "background_color": "#FFFFFF",
                            "image_url": ""
                        },
                        "content": {
                            "title": "",
                            "subtitle": "",
                            "bullets": [],
                            "cta_label": "",
                            "price_table": [],
                            "form_fields": []
                        },
                        "notes": ""
                    }
                    
                    st.success("✅ 基本情報を保存しました！「Step 2」でプロンプトを生成してください。")
        
        with col2:
            st.markdown("### 💡 ヒント")
            st.info("""
            **テンプレート名のコツ**
            - ターゲット業界を含める
            - デザインの特徴を一言で
            
            **タグ付けのコツ**
            - 業界（BtoB, EC, 採用）
            - デザイン（シンプル, リッチ）
            - 用途（リード獲得, 認知）
            """)
    
    # Step 2: プロンプト生成
    with tab2:
        st.markdown("### ChatGPT用プロンプト生成")
        
        if "draft_template" not in st.session_state:
            st.warning("⚠️ 先に「Step 1」で基本情報を入力してください")
        else:
            draft = st.session_state.draft_template
            
            st.success(f"✅ テンプレート「{draft['display_name']}」の基本情報を読み込みました")
            
            # プロンプト生成
            prompt = f"""以下のLP事例を、テンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {draft['display_name']}
- セクション種別: {draft['section_type']}
- 参照URL: {draft['metadata']['source_url']}
- 説明: {draft['metadata']['description']}

【出力すべきJSON項目】
```json
{{
  "title": "メインコピー（必須）",
  "subtitle": "サブコピー",
  "bullets": ["箇条書き1", "箇条書き2"],
  "cta_label": "CTAボタンのテキスト",
  "alignment": "center",
  "background_color": "#FFFFFF"
}}
```

【注意事項】
- 著作権に配慮し、コピーは抽象化・一般化してください
- 構造とレイアウトのパターンのみを抽出してください
- 固有名詞は汎用的な表現に置き換えてください
- {draft['section_type']}セクションとして機能する内容にしてください

上記JSON形式で出力してください。
"""
            
            st.code(prompt, language="text")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📋 プロンプトをダウンロード",
                    data=prompt,
                    file_name="chatgpt_prompt.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("➡️ Step 3へ進む", type="primary", use_container_width=True):
                    st.info("「Step 3: JSON入力・プレビュー」タブに移動してください")
    
    # Step 3: JSON入力・プレビュー
    with tab3:
        st.markdown("### JSON入力・プレビュー")
        
        if "draft_template" not in st.session_state:
            st.warning("⚠️ 先に「Step 1」で基本情報を入力してください")
        else:
            draft = st.session_state.draft_template
            
            st.info(f"💡 ChatGPTから返ってきたJSONを貼り付けてください（テンプレート：{draft['display_name']}）")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### JSON入力")
                
                json_input = st.text_area(
                    "ChatGPT出力JSON",
                    height=300,
                    placeholder='{\n  "title": "...",\n  "subtitle": "...",\n  ...\n}',
                    key="json_input"
                )
                
                if st.button("👁️ プレビュー生成", use_container_width=True):
                    try:
                        # JSON解析
                        content_data = json.loads(json_input)
                        
                        # ドラフトテンプレートを更新
                        st.session_state.draft_template["content"].update(content_data)
                        if "alignment" in content_data:
                            st.session_state.draft_template["layout"]["alignment"] = content_data["alignment"]
                        if "background_color" in content_data:
                            st.session_state.draft_template["layout"]["background_color"] = content_data["background_color"]
                        
                        st.success("✅ JSONを解析しました。右側でプレビューを確認してください。")
                        st.session_state.show_preview = True
                        
                    except json.JSONDecodeError as e:
                        st.error(f"⚠️ JSON形式エラー: {str(e)}")
                    except Exception as e:
                        st.error(f"⚠️ エラー: {str(e)}")
            
            with col2:
                st.markdown("#### プレビュー")
                
                if st.session_state.get("show_preview", False):
                    # プレビュー表示
                    html_preview = generate_template_preview(st.session_state.draft_template)
                    st.components.v1.html(html_preview, height=400, scrolling=True)
                    
                    st.markdown("---")
                    
                    # 承認アクション
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ 承認してテンプレート登録", type="primary", use_container_width=True):
                            st.session_state.draft_template["status"] = "approved"
                            add_template(st.session_state.draft_template)
                            
                            st.success("🎉 テンプレートを承認・登録しました！")
                            st.balloons()
                            
                            # クリーンアップ
                            del st.session_state.draft_template
                            del st.session_state.show_preview
                            st.rerun()
                    
                    with col_b:
                        if st.button("📝 下書きとして保存", use_container_width=True):
                            add_template(st.session_state.draft_template)
                            
                            st.success("💾 下書きとして保存しました。「テンプレート一覧」から編集できます。")
                            
                            # クリーンアップ
                            del st.session_state.draft_template
                            del st.session_state.show_preview
                            st.rerun()
                else:
                    st.info("左側でJSONを入力して「プレビュー生成」ボタンを押してください")

def show_page_builder():
    """LP作成画面"""
    st.markdown("## 🎨 LP作成")
    st.markdown("承認済みテンプレートを組み合わせてLP全体を作成します。")
    
    # 承認済みテンプレートのみ取得
    templates = get_templates()
    approved_templates = [t for t in templates if t["status"] == "approved"]
    
    if not approved_templates:
        st.warning("⚠️ 承認済みテンプレートがありません。先に「テンプレート登録」から作成してください。")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Step 1: ページ条件設定")
        
        page_type = st.selectbox(
            "ページタイプ",
            ["BtoB SaaSリード獲得", "採用LP", "セミナー集客", "EC商品LP"]
        )
        
        target = st.text_area(
            "ターゲット",
            placeholder="例: マーケ責任者 / リードはあるが受注につながらない層",
            height=80
        )
        
        tone = st.selectbox("トンマナ", ["かっちり", "カジュアル", "テックっぽい", "温かみ"])
        
        brand_color = st.color_picker("ブランドカラー", "#2563EB")
        
        st.markdown("---")
        st.markdown("### Step 2: セクション選択")
        
        # セクション別にテンプレート選択
        sections = {}
        section_types = ["header", "trouble", "pricing", "cta"]
        section_labels = {
            "header": "ヘッダー",
            "trouble": "お悩み",
            "pricing": "価格表",
            "cta": "CTA"
        }
        
        for section_type in section_types:
            templates_of_type = [t for t in approved_templates if t["section_type"] == section_type]
            
            if templates_of_type:
                template_options = {t["display_name"]: t for t in templates_of_type}
                selected_name = st.selectbox(
                    f"📌 {section_labels[section_type]}",
                    options=list(template_options.keys())
                )
                sections[section_type] = template_options[selected_name]
    
    with col2:
        st.markdown("### Step 3: プレビュー")
        
        if st.button("🎨 LPプレビュー生成", type="primary", use_container_width=True):
            st.markdown("#### ワイヤーフレーム")
            
            # テキストベースのワイヤーフレーム
            wireframe = ""
            for i, (section_type, template) in enumerate(sections.items(), 1):
                wireframe += f"\n**{i}. {section_labels[section_type]}**\n"
                wireframe += f"- メインコピー: {template['content']['title']}\n"
                wireframe += f"- サブコピー: {template['content']['subtitle']}\n"
                if template['content']['cta_label']:
                    wireframe += f"- CTA: {template['content']['cta_label']}\n"
            
            st.text_area("テキスト構造", wireframe, height=200)
            
            st.markdown("---")
            st.markdown("#### デザインプレビュー")
            
            # 統合HTMLプレビュー
            html_preview = '<div style="max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
            
            for section_type, template in sections.items():
                html_preview += generate_template_preview(template, brand_color).replace('<div style="max-width: 1200px; margin: 0 auto;', '<div style="').replace('</div>', '', 1)
            
            html_preview += "</div>"
            
            st.components.v1.html(html_preview, height=800, scrolling=True)
            
            st.markdown("---")
            st.markdown("#### コード出力")
            
            with st.expander("📥 HTML/CSSコードを表示"):
                st.code(html_preview, language="html")
                
                st.download_button(
                    label="💾 HTMLをダウンロード",
                    data=html_preview,
                    file_name="lp_preview.html",
                    mime="text/html"
                )

def show_template_list():
    """テンプレート一覧画面"""
    st.markdown("## 📚 テンプレート一覧")
    
    templates = get_templates()
    
    if not templates:
        st.info("まだテンプレートがありません。「テンプレート登録」から作成してください。")
        return
    
    # フィルター
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("ステータス", ["all", "draft", "approved", "need_fix"])
    with col2:
        section_filter = st.selectbox("セクション種別", ["all", "header", "trouble", "pricing", "cta", "form"])
    
    # フィルタリング
    filtered = templates
    if status_filter != "all":
        filtered = [t for t in filtered if t["status"] == status_filter]
    if section_filter != "all":
        filtered = [t for t in filtered if t["section_type"] == section_filter]
    
    st.markdown(f"### 📊 {len(filtered)}件のテンプレート")
    
    # テンプレートカード表示
    for template in filtered:
        status_colors = {
            "draft": ("bg-yellow-100", "text-yellow-800"),
            "approved": ("bg-green-100", "text-green-800"),
            "need_fix": ("bg-red-100", "text-red-800")
        }
        bg_class, text_class = status_colors.get(template["status"], ("bg-gray-100", "text-gray-800"))
        
        with st.container():
            st.markdown(f"""
            <div class="bg-white rounded-lg shadow-md p-6 mb-4 border border-gray-200">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">{template['display_name']}</h3>
                        <p class="text-gray-600 mt-2">{template['metadata']['description']}</p>
                    </div>
                    <span class="px-3 py-1 {bg_class} {text_class} rounded-full text-sm font-semibold">
                        {template['status']}
                    </span>
                </div>
                <div class="flex gap-2 mb-3">
                    <span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">{template['section_type']}</span>
                    {''.join([f'<span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{tag}</span>' for tag in template['metadata']['tags']])}
                </div>
                <div class="text-sm text-gray-500">
                    作成日: {template['metadata']['created_at']} | ID: {template['template_id'][:8]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # アクション
            col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
            with col1:
                if st.button("👁️ 表示", key=f"view_{template['template_id']}"):
                    st.session_state.editing_template_id = template['template_id']
                    st.rerun()
            with col2:
                if template["status"] == "draft":
                    if st.button("✅ 承認", key=f"approve_{template['template_id']}"):
                        update_template(template['template_id'], {"status": "approved"})
                        st.success("承認しました！")
                        st.rerun()
            with col3:
                if st.button("🗑️ 削除", key=f"delete_{template['template_id']}"):
                    delete_template(template['template_id'])
                    st.success("削除しました！")
                    st.rerun()
    
    # テンプレート詳細モーダル
    if st.session_state.editing_template_id:
        show_template_detail_modal()

def show_template_detail_modal():
    """テンプレート詳細・編集モーダル"""
    template_id = st.session_state.editing_template_id
    template = get_template_by_id(template_id)
    
    if not template:
        st.error("テンプレートが見つかりません")
        st.session_state.editing_template_id = None
        return
    
    # モーダル風表示
    st.markdown("---")
    st.markdown(f"## 📝 テンプレート詳細: {template['display_name']}")
    
    col_close, _ = st.columns([1, 5])
    with col_close:
        if st.button("❌ 閉じる"):
            st.session_state.editing_template_id = None
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["👁️ プレビュー", "✏️ 編集", "📋 JSON"])
    
    # プレビュータブ
    with tab1:
        st.markdown("### プレビュー")
        html_preview = generate_template_preview(template)
        st.components.v1.html(html_preview, height=500, scrolling=True)
    
    # 編集タブ
    with tab2:
        st.markdown("### コンテンツ編集")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("タイトル", value=template['content'].get('title', ''), key="edit_title")
            new_subtitle = st.text_area("サブタイトル", value=template['content'].get('subtitle', ''), height=80, key="edit_subtitle")
            new_cta = st.text_input("CTAラベル", value=template['content'].get('cta_label', ''), key="edit_cta")
        
        with col2:
            new_alignment = st.selectbox("配置", ["left", "center", "right"], 
                                        index=["left", "center", "right"].index(template['layout'].get('alignment', 'center')),
                                        key="edit_align")
            new_bg_color = st.color_picker("背景色", value=template['layout'].get('background_color', '#FFFFFF'), key="edit_bg")
        
        if st.button("💾 更新を保存", type="primary"):
            updates = {
                "content": {
                    **template['content'],
                    "title": new_title,
                    "subtitle": new_subtitle,
                    "cta_label": new_cta
                },
                "layout": {
                    **template['layout'],
                    "alignment": new_alignment,
                    "background_color": new_bg_color
                }
            }
            update_template(template_id, updates)
            st.success("✅ 更新しました！")
            st.rerun()
    
    # JSONタブ
    with tab3:
        st.markdown("### JSON表示")
        st.json(template)
        
        st.download_button(
            label="💾 JSONをダウンロード",
            data=json.dumps(template, ensure_ascii=False, indent=2),
            file_name=f"template_{template['template_id']}.json",
            mime="application/json"
        )

def show_data_management():
    """データ管理画面"""
    st.markdown("## 💾 データ管理")
    st.markdown("テンプレートデータのエクスポート・インポートができます。")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 エクスポート")
        st.info("現在のテンプレートデータをJSON形式でダウンロードできます。")
        
        json_data = export_templates_json()
        
        st.download_button(
            label="💾 JSONをダウンロード",
            data=json_data,
            file_name=f"templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        with st.expander("📋 JSONプレビュー"):
            st.code(json_data, language="json")
    
    with col2:
        st.markdown("### 📥 インポート")
        st.info("以前エクスポートしたJSONファイルを読み込めます。")
        
        uploaded_file = st.file_uploader("JSONファイルを選択", type=["json"])
        
        if uploaded_file is not None:
            try:
                imported_data = json.load(uploaded_file)
                
                if "templates" in imported_data:
                    st.success(f"✅ {len(imported_data['templates'])}件のテンプレートを読み込みました")
                    
                    if st.button("📥 インポート実行", type="primary", use_container_width=True):
                        st.session_state.templates = imported_data["templates"]
                        st.success("インポートが完了しました！")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("⚠️ 正しいJSON形式ではありません")
            except Exception as e:
                st.error(f"⚠️ エラー: {str(e)}")

# ===== エントリーポイント =====

if __name__ == "__main__":
    main()
