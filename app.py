import streamlit as st
import json
import re
import html
from pathlib import Path
from datetime import datetime
import uuid
import base64

# ページ設定
st.set_page_config(
    page_title="LP Template Manager - Smart Backup",
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== スマートバックアップ機能 =====

def show_smart_backup_alert(template_data):
    """
    新規テンプレート作成時のスマートバックアップアラート
    1クリックでコピー＆ダウンロード機能付き
    """
    template_name = template_data.get('name', '新規テンプレート')
    
    # アラート表示条件チェック
    if not st.session_state.get('show_backup_alerts', True):
        return
    
    # カスタムCSS for アラート
    st.markdown("""
    <style>
    .backup-alert {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .backup-alert h3 {
        color: #fff !important;
        margin-bottom: 10px;
    }
    .backup-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    .backup-btn {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    .backup-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }
    .copy-success {
        color: #10B981 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # アラートHTML
    alert_html = f"""
    <div class="backup-alert">
        <h3>🎉 テンプレート「{html.escape(template_name)}」を保存しました！</h3>
        <p>💡 <strong>今すぐバックアップしませんか？</strong> 
        データが消失する前に、1クリックで安全に保存できます。</p>
        
        <div class="backup-buttons">
            <button class="backup-btn" onclick="copyToClipboard()" id="copyBtn">
                📋 クリップボードにコピー
            </button>
            <button class="backup-btn" onclick="downloadTemplate()" id="downloadBtn">
                💾 ファイルでダウンロード
            </button>
            <button class="backup-btn" onclick="copyAllTemplates()" id="copyAllBtn">
                📦 全テンプレートをコピー
            </button>
        </div>
        
        <p style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
        💭 このアラートは設定で無効にできます
        </p>
    </div>
    
    <script>
    // 個別テンプレートをクリップボードにコピー
    function copyToClipboard() {{
        const templateData = {json.dumps(template_data, ensure_ascii=False)};
        const jsonString = JSON.stringify(templateData, null, 2);
        
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(jsonString).then(function() {{
                document.getElementById('copyBtn').innerHTML = '✅ コピー完了！';
                document.getElementById('copyBtn').classList.add('copy-success');
                setTimeout(() => {{
                    document.getElementById('copyBtn').innerHTML = '📋 クリップボードにコピー';
                    document.getElementById('copyBtn').classList.remove('copy-success');
                }}, 2000);
            }}).catch(function() {{
                fallbackCopy(jsonString);
            }});
        }} else {{
            fallbackCopy(jsonString);
        }}
    }}
    
    // 個別テンプレートをダウンロード
    function downloadTemplate() {{
        const templateData = {json.dumps(template_data, ensure_ascii=False)};
        const jsonString = JSON.stringify(templateData, null, 2);
        const blob = new Blob([jsonString], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `template_{template_data.get('name', 'unnamed').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        document.getElementById('downloadBtn').innerHTML = '✅ ダウンロード完了！';
        setTimeout(() => {{
            document.getElementById('downloadBtn').innerHTML = '💾 ファイルでダウンロード';
        }}, 2000);
    }}
    
    // 全テンプレートをクリップボードにコピー
    function copyAllTemplates() {{
        const allTemplates = {json.dumps(st.session_state.templates, ensure_ascii=False)};
        const exportData = {{
            'export_date': new Date().toISOString(),
            'version': '1.0',
            'total_templates': Object.keys(allTemplates).length,
            'templates': allTemplates
        }};
        const jsonString = JSON.stringify(exportData, null, 2);
        
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(jsonString).then(function() {{
                document.getElementById('copyAllBtn').innerHTML = '✅ 全データコピー完了！';
                setTimeout(() => {{
                    document.getElementById('copyAllBtn').innerHTML = '📦 全テンプレートをコピー';
                }}, 2000);
            }});
        }}
    }}
    
    // フォールバック用コピー関数
    function fallbackCopy(text) {{
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {{
            document.execCommand('copy');
            document.getElementById('copyBtn').innerHTML = '✅ コピー完了！';
        }} catch (err) {{
            document.getElementById('copyBtn').innerHTML = '❌ コピー失敗';
        }}
        document.body.removeChild(textArea);
    }}
    </script>
    """
    
    st.markdown(alert_html, unsafe_allow_html=True)

def create_quick_backup_sidebar():
    """
    サイドバーのクイックバックアップ機能
    """
    st.sidebar.markdown("---")
    st.sidebar.write("### ⚡ クイックバックアップ")
    
    template_count = len(st.session_state.templates) if st.session_state.templates else 0
    
    if template_count > 0:
        # 1クリック全コピー
        if st.sidebar.button("📋 全テンプレート即コピー", help="クリップボードに全データをコピー"):
            show_clipboard_copy_success()
        
        # 1クリック全ダウンロード  
        backup_data = create_backup_data()
        if backup_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lp_templates_backup_{timestamp}.json"
            
            st.sidebar.download_button(
                label="💾 全テンプレート即DL",
                data=backup_data,
                file_name=filename,
                mime="application/json",
                help="ワンクリックで全テンプレートをダウンロード"
            )
        
        # 最新テンプレートのクイックアクション
        if st.session_state.templates:
            latest_template = get_latest_template()
            if latest_template:
                st.sidebar.write(f"**最新**: {latest_template.get('name', '無名')[:15]}...")
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("📋", key="quick_copy_latest", help="最新テンプレートをコピー"):
                        show_single_template_copy(latest_template)
                
                with col2:
                    # 個別ダウンロード
                    template_json = json.dumps(latest_template, ensure_ascii=False, indent=2)
                    template_name = latest_template.get('name', 'template').replace(' ', '_')
                    filename = f"template_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    st.download_button(
                        label="💾",
                        data=template_json.encode('utf-8'),
                        file_name=filename,
                        mime="application/json",
                        key="quick_dl_latest",
                        help="最新テンプレートをダウンロード"
                    )
    
    else:
        st.sidebar.info("テンプレートがありません")
    
    # アラート設定
    st.sidebar.markdown("---")
    st.sidebar.write("### ⚙️ アラート設定")
    
    show_alerts = st.sidebar.checkbox(
        "バックアップアラートを表示",
        value=st.session_state.get('show_backup_alerts', True),
        help="新規テンプレート作成時のアラート表示"
    )
    st.session_state.show_backup_alerts = show_alerts
    
    auto_backup = st.sidebar.checkbox(
        "自動バックアップ（localStorage）",
        value=st.session_state.get('auto_backup', True),
        help="ブラウザのローカルストレージに自動保存"
    )
    st.session_state.auto_backup = auto_backup

def show_clipboard_copy_success():
    """
    クリップボードコピー成功の表示
    """
    # JavaScriptでクリップボードにコピー
    all_templates_json = json.dumps({
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'total_templates': len(st.session_state.templates),
        'templates': st.session_state.templates
    }, ensure_ascii=False, indent=2)
    
    copy_js = f"""
    <script>
    const data = {json.dumps(all_templates_json)};
    if (navigator.clipboard) {{
        navigator.clipboard.writeText(data).then(function() {{
            alert('✅ 全テンプレートをクリップボードにコピーしました！\\n\\n💡 任意の場所に貼り付けて保存してください。');
        }}).catch(function() {{
            console.log('クリップボードコピーに失敗しました');
        }});
    }}
    </script>
    """
    st.components.v1.html(copy_js, height=0)

def show_single_template_copy(template):
    """
    個別テンプレートのクリップボードコピー
    """
    template_json = json.dumps(template, ensure_ascii=False, indent=2)
    
    copy_js = f"""
    <script>
    const data = {json.dumps(template_json)};
    if (navigator.clipboard) {{
        navigator.clipboard.writeText(data).then(function() {{
            alert('✅ テンプレート「{template.get("name", "無名")}」をコピーしました！');
        }});
    }}
    </script>
    """
    st.components.v1.html(copy_js, height=0)

def get_latest_template():
    """
    最新のテンプレートを取得
    """
    if not st.session_state.templates:
        return None
    
    # created_atでソート
    templates = list(st.session_state.templates.values())
    templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return templates[0] if templates else None

def create_backup_data():
    """
    バックアップデータを作成
    """
    if not st.session_state.templates:
        return None
    
    export_data = {
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'total_templates': len(st.session_state.templates),
        'templates': st.session_state.templates
    }
    
    return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')

# ===== 自動バックアップシステム =====

def setup_auto_backup():
    """
    自動バックアップシステムのセットアップ
    """
    if not st.session_state.get('auto_backup', True):
        return
    
    auto_backup_js = f"""
    <script>
    // 自動バックアップ関数
    function autoBackup() {{
        const templates = {json.dumps(st.session_state.templates)};
        if (Object.keys(templates).length > 0) {{
            try {{
                localStorage.setItem('lp_templates_auto_backup', JSON.stringify({{
                    timestamp: new Date().toISOString(),
                    templates: templates
                }}));
                console.log('Auto backup completed');
            }} catch(e) {{
                console.error('Auto backup failed:', e);
            }}
        }}
    }}
    
    // ページ読み込み時とテンプレート変更時に自動バックアップ
    autoBackup();
    
    // 定期的な自動バックアップ（5分間隔）
    setInterval(autoBackup, 300000);
    </script>
    """
    st.components.v1.html(auto_backup_js, height=0)

def show_backup_status():
    """
    バックアップ状況の表示
    """
    template_count = len(st.session_state.templates) if st.session_state.templates else 0
    
    if template_count > 0:
        # 最後のバックアップ時刻表示
        if 'last_backup_time' in st.session_state:
            last_backup = st.session_state.last_backup_time
            st.sidebar.success(f"📅 最終バックアップ: {last_backup.strftime('%H:%M:%S')}")
        
        # バックアップ推奨アラート
        if template_count >= 3 and not st.session_state.get('backup_reminded', False):
            st.sidebar.warning("⚠️ 3個以上のテンプレートがあります。バックアップをお勧めします！")
            if st.sidebar.button("今すぐバックアップ"):
                st.session_state.backup_reminded = True

# ===== セキュリティ＆ユーティリティ関数（簡略版） =====

def sanitize_html(content):
    """HTMLサニタイズ（簡略版）"""
    if not isinstance(content, str):
        return str(content)
    return html.escape(content)

def safe_get_nested(data, path, default=None):
    """ネストされたJSONから値を安全に取得"""
    try:
        if not isinstance(data, dict):
            return default
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current if current is not None else default
    except Exception:
        return default

def init_session_state():
    """セッションステート初期化"""
    if 'templates' not in st.session_state:
        st.session_state.templates = {}
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = None
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "template_registration"
    if 'show_backup_alerts' not in st.session_state:
        st.session_state.show_backup_alerts = True
    if 'auto_backup' not in st.session_state:
        st.session_state.auto_backup = True

def save_template(template_data):
    """
    テンプレートを安全に保存（スマートアラート付き）
    """
    try:
        if not isinstance(template_data, dict):
            st.error("無効なテンプレートデータです")
            return False
        
        if not template_data.get('name'):
            st.error("テンプレート名が必要です")
            return False
        
        template_id = str(uuid.uuid4())
        template_data['id'] = template_id
        template_data['created_at'] = datetime.now().isoformat()
        
        # セッションステートに保存
        st.session_state.templates[template_id] = template_data
        
        # 最終バックアップ時刻を更新
        st.session_state.last_backup_time = datetime.now()
        
        # 成功メッセージ（通常のst.success は非表示）
        # st.success("テンプレートが保存されました")
        
        # スマートバックアップアラートを表示
        show_smart_backup_alert(template_data)
        
        return True
    
    except Exception as e:
        st.error(f"保存エラー: {str(e)}")
        return False

# CSS & セクション定義
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #F9FAFB; }
    iframe { 
        width: 100% !important; 
        border: 1px solid #E5E7EB; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
    }
</style>
""", unsafe_allow_html=True)

SECTION_CATEGORIES = {
    "🏠 ヘッダー・導入": {
        "hero": "ヒーローセクション",
        "header": "シンプルヘッダー"
    },
    "⚡ 課題・価値提案": {
        "trouble": "お悩み・課題", 
        "features": "機能紹介",
        "how_it_works": "利用の流れ"
    },
    "🏆 信頼・実績": {
        "testimonials": "お客様の声",
        "social_proof": "導入企業"
    },
    "💰 料金・申し込み": {
        "pricing": "料金表",
        "cta": "CTA・申し込み", 
        "faq": "よくある質問"
    }
}

SECTION_LABELS = {
    "hero": "ヒーローセクション",
    "header": "シンプルヘッダー",
    "trouble": "お悩み・課題", 
    "features": "機能紹介",
    "how_it_works": "利用の流れ",
    "testimonials": "お客様の声", 
    "social_proof": "導入企業",
    "pricing": "料金表",
    "cta": "CTA・申し込み",
    "faq": "よくある質問"
}

# ===== 簡易版エディター =====

def show_simple_editor(template):
    """簡易版エディター"""
    st.subheader("✏️ テンプレート編集")
    
    section_type = template.get('section_type', 'hero')
    st.write(f"**セクション**: {SECTION_LABELS.get(section_type, section_type)}")
    
    # 基本情報編集
    name = st.text_input("テンプレート名", value=template.get('name', ''), key="edit_name")
    description = st.text_area("説明", value=template.get('description', ''), key="edit_description")
    
    # JSONデータ表示・編集
    st.write("### 📄 JSONデータ")
    json_str = json.dumps(template, ensure_ascii=False, indent=2)
    edited_json = st.text_area("JSONデータ", value=json_str, height=200, key="edit_json")
    
    # 保存ボタン
    if st.button("💾 変更を保存", key="save_changes"):
        try:
            # JSON解析
            updated_data = json.loads(edited_json)
            updated_data['name'] = name
            updated_data['description'] = description
            updated_data['updated_at'] = datetime.now().isoformat()
            
            # セッションステートを更新
            template_id = template.get('id')
            if template_id and template_id in st.session_state.templates:
                st.session_state.templates[template_id] = updated_data
                
                # 更新成功時もスマートアラート表示
                show_smart_backup_alert(updated_data)
                st.rerun()
            else:
                st.error("テンプレートIDが見つかりません")
        
        except json.JSONDecodeError as e:
            st.error(f"JSON形式が正しくありません: {str(e)}")
        except Exception as e:
            st.error(f"保存エラー: {str(e)}")

# ===== メインアプリケーション =====

def main():
    """メインアプリケーション（スマートバックアップ版）"""
    try:
        # セッション初期化
        init_session_state()
        
        # 自動バックアップセットアップ
        setup_auto_backup()
        
        # ヘッダー
        st.title("⚡ LP Template Manager - Smart Backup")
        st.markdown("**1クリックバックアップ・自動保存機能付き**")
        
        # サイドバー
        with st.sidebar:
            st.header("🎛️ 操作パネル")
            
            mode = st.selectbox(
                "モード選択",
                ["template_registration", "design_creation"],
                format_func=lambda x: "📝 テンプレート登録" if x == "template_registration" else "🎨 デザイン作成",
                key="mode_selector"
            )
            
            st.session_state.current_mode = mode
            
            # クイックバックアップUI
            create_quick_backup_sidebar()
            
            # バックアップ状況表示
            show_backup_status()
        
        # モード別処理
        if st.session_state.current_mode == "template_registration":
            show_template_registration_mode()
        else:
            show_design_creation_mode()
    
    except Exception as e:
        st.error(f"アプリケーションエラー: {str(e)}")

def show_template_registration_mode():
    """テンプレート登録モード"""
    st.header("📝 テンプレート登録モード")
    
    col1, col2 = st.columns(2)
    
    with col1:
        template_name = st.text_input("テンプレート名", key="template_name")
        reference_url = st.text_input("参考URL", key="reference_url")
    
    with col2:
        section_type = st.selectbox(
            "セクション種別",
            list(SECTION_LABELS.keys()),
            format_func=lambda x: SECTION_LABELS[x],
            key="section_type"
        )
        description = st.text_area("説明", key="template_description")
    
    # JSON入力
    json_input = st.text_area("JSONデータを入力", height=150, key="json_input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 JSONをパース", key="parse_json"):
            try:
                if json_input.strip():
                    parsed_data = json.loads(json_input)
                    
                    template_data = {
                        'name': template_name or f"テンプレート_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'section_type': section_type,
                        'reference_url': reference_url,
                        'description': description,
                        'created_at': datetime.now().isoformat(),
                        **parsed_data
                    }
                    
                    st.session_state.temp_template = template_data
                    st.success("JSONデータをパースしました！")
                else:
                    st.error("JSONデータを入力してください")
                    
            except json.JSONDecodeError as e:
                st.error(f"JSON解析エラー: {str(e)}")
    
    with col2:
        if st.button("💾 テンプレート保存", key="save_template"):
            if 'temp_template' in st.session_state:
                success = save_template(st.session_state.temp_template)
                if success:
                    # temp_templateを削除（スマートアラート表示後）
                    if 'temp_template' in st.session_state:
                        del st.session_state.temp_template
            else:
                st.error("先にJSONをパースしてください")
    
    # 保存済みテンプレート一覧
    if st.session_state.templates:
        st.write("### 📚 保存済みテンプレート")
        for template_id, template in st.session_state.templates.items():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{template.get('name', '無名')}** ({SECTION_LABELS.get(template.get('section_type', 'unknown'), '不明')})")
            with col2:
                if st.button("編集", key=f"edit_{template_id}"):
                    st.session_state.selected_template = template_id
                    st.session_state.current_mode = "design_creation"
                    st.rerun()
            with col3:
                # 個別コピー
                if st.button("📋", key=f"copy_{template_id}", help="コピー"):
                    show_single_template_copy(template)
            with col4:
                if st.button("🗑️", key=f"delete_{template_id}", help="削除"):
                    del st.session_state.templates[template_id]
                    st.rerun()

def show_design_creation_mode():
    """デザイン作成モード"""
    st.header("🎨 デザイン作成モード")
    
    if not st.session_state.templates:
        st.warning("テンプレートが登録されていません。まずはテンプレート登録モードでテンプレートを作成してください。")
        return
    
    # テンプレート選択
    template_options = {
        template_id: f"{template.get('name', '無名')} ({SECTION_LABELS.get(template.get('section_type', 'unknown'), '不明')})"
        for template_id, template in st.session_state.templates.items()
    }
    
    selected_id = st.selectbox(
        "編集するテンプレートを選択",
        list(template_options.keys()),
        format_func=lambda x: template_options[x],
        key="template_selector"
    )
    
    if selected_id:
        template = st.session_state.templates[selected_id]
        show_simple_editor(template)

if __name__ == "__main__":
    main()
