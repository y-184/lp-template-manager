import streamlit as st
import json
import re
import html
from datetime import datetime
import uuid

# ページ設定
st.set_page_config(
    page_title="LP Template Manager - Cyberpunk Edition",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== サイバーパンク風スタイル =====

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
    /* サイバーパンク背景 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 25%, #16213e 50%, #0a0e27 100%);
        background-attachment: fixed;
        position: relative;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            repeating-linear-gradient(0deg, rgba(255,0,255,0.03) 0px, transparent 2px, transparent 4px),
            repeating-linear-gradient(90deg, rgba(0,255,255,0.03) 0px, transparent 2px, transparent 4px);
        pointer-events: none;
        z-index: 0;
    }
    
    /* グローバルテキストカラー */
    .stApp, .stApp * {
        color: #e0e7ff !important;
    }
    
    /* タブスタイル改善 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 30, 60, 0.8);
        padding: 12px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 255, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: rgba(20, 20, 40, 0.6);
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 600;
        font-size: 15px;
        color: #a0aec0 !important;
        border: 1px solid rgba(100, 100, 150, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(30, 30, 60, 0.8);
        border-color: rgba(0, 255, 255, 0.5);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%) !important;
        color: white !important;
        border-color: transparent;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }
    
    /* 入力欄スタイル */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        color: #e0e7ff !important;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(0, 255, 255, 0.8) !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3) !important;
    }
    
    /* ラベルスタイル */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #00d4ff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* ボタンスタイル */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
    }
    
    /* プロンプトボックス */
    .prompt-box {
        background: rgba(20, 20, 40, 0.9);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        line-height: 1.8;
        color: #00ff88 !important;
        max-height: 400px;
        overflow-y: auto;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
    }
    
    /* ヘルプボックス */
    .help-box {
        background: rgba(0, 100, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }
    
    .help-box strong {
        color: #00d4ff !important;
    }
    
    /* バックアップアラート */
    .backup-alert {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
        border: 2px solid rgba(0, 255, 136, 0.5);
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
    }
    
    .backup-alert h3 {
        color: #00ff88 !important;
        margin-bottom: 12px;
        font-size: 20px;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    /* コピーボタン */
    .cyber-button {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .cyber-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
    }
    
    /* エクスパンダー */
    .streamlit-expanderHeader {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        color: #e0e7ff !important;
    }
    
    /* プレビューiframe */
    iframe {
        border: 2px solid rgba(0, 255, 255, 0.5) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 40px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* サクセス/エラーメッセージ */
    .stSuccess, .stError, .stWarning, .stInfo {
        background: rgba(20, 20, 40, 0.8) !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(10px);
    }
    
    /* JSONプレビュー */
    pre {
        background: rgba(20, 20, 40, 0.9) !important;
        border: 1px solid rgba(0, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: #00ff88 !important;
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
  "title": "メインタイトル（20-40文字）",
  "subtitle": "サブタイトル（40-80文字）",
  "description": "詳細説明（100-200文字）",
  "cta_primary": "主要CTAボタンテキスト",
  "cta_secondary": "副次CTAボタンテキスト",
  "hero_image_description": "ヒーロー画像の説明",
  "trust_elements": ["信頼要素1", "信頼要素2"],
  "background_style": "背景スタイル",
  "layout_type": "レイアウトタイプ"
}}
```

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
  "section_title": "セクションタイトル",
  "introduction": "導入文",
  "features": [
    {{
      "title": "機能1のタイトル",
      "description": "機能1の詳細説明",
      "icon": "アイコン（例: ⚡）"
    }}
  ]
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
  "section_title": "セクションタイトル",
  "testimonials": [
    {{
      "quote": "お客様のコメント",
      "author": "氏名",
      "company": "企業名",
      "position": "役職"
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
  "section_title": "セクションタイトル",
  "companies": ["企業名1", "企業名2"],
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
  "section_title": "セクションタイトル",
  "questions": [
    {{
      "question": "質問1",
      "answer": "回答1"
    }}
  ]
}}
```

上記JSON形式で出力してください。
"""
}

SECTION_LABELS = {
    "hero": "🚀 ヒーローセクション",
    "features": "⚡ 機能紹介",
    "testimonials": "💬 お客様の声",
    "social_proof": "🏆 導入企業",
    "faq": "❓ よくある質問"
}

# ===== HTML生成関数 =====

def generate_section_preview(template):
    """セクションのHTMLプレビューを生成"""
    section_type = template.get('section_type', 'hero')
    
    if section_type == 'hero':
        return generate_hero_preview(template)
    elif section_type == 'features':
        return generate_features_preview(template)
    elif section_type == 'testimonials':
        return generate_testimonials_preview(template)
    elif section_type == 'social_proof':
        return generate_social_proof_preview(template)
    elif section_type == 'faq':
        return generate_faq_preview(template)
    else:
        return "<p>プレビュー生成中...</p>"

def generate_hero_preview(template):
    """ヒーローセクションのプレビュー生成"""
    title = template.get('title', 'タイトル')
    subtitle = template.get('subtitle', 'サブタイトル')
    description = template.get('description', '説明文')
    cta_primary = template.get('cta_primary', '無料で始める')
    cta_secondary = template.get('cta_secondary', '資料請求')
    trust_elements = template.get('trust_elements', [])
    
    trust_html = ""
    if trust_elements:
        badges = [f"<span style='background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 8px 16px; border-radius: 20px; font-size: 14px; border: 1px solid rgba(59, 130, 246, 0.3);'>{elem}</span>" 
                 for elem in trust_elements]
        trust_html = f"<div style='display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-top: 24px;'>{''.join(badges)}</div>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px;
            }}
            .container {{
                max-width: 1200px;
                text-align: center;
                color: white;
            }}
            h1 {{
                font-size: clamp(2rem, 5vw, 4rem);
                font-weight: 800;
                margin-bottom: 24px;
                line-height: 1.2;
            }}
            .subtitle {{
                font-size: clamp(1rem, 2vw, 1.5rem);
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 16px;
                font-weight: 500;
            }}
            .description {{
                font-size: 1.1rem;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 32px;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            .cta-buttons {{
                display: flex;
                gap: 16px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 24px;
            }}
            .cta-primary {{
                background: white;
                color: #667eea;
                padding: 16px 48px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 1.1rem;
                border: none;
                cursor: pointer;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            }}
            .cta-secondary {{
                background: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 16px 48px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 1.1rem;
                border: 2px solid white;
                cursor: pointer;
                backdrop-filter: blur(10px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
            <div class="description">{description}</div>
            <div class="cta-buttons">
                <button class="cta-primary">{cta_primary}</button>
                <button class="cta-secondary">{cta_secondary}</button>
            </div>
            {trust_html}
        </div>
    </body>
    </html>
    """

def generate_features_preview(template):
    """機能セクションのプレビュー生成"""
    section_title = template.get('section_title', '主要機能')
    introduction = template.get('introduction', '')
    features = template.get('features', [])
    
    features_html = ""
    for feature in features:
        features_html += f"""
        <div style='background: white; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            <div style='font-size: 2.5rem; margin-bottom: 16px;'>{feature.get('icon', '⚡')}</div>
            <h3 style='font-size: 1.5rem; color: #1f2937; margin-bottom: 12px; font-weight: 700;'>{feature.get('title', '機能名')}</h3>
            <p style='color: #6b7280; line-height: 1.6;'>{feature.get('description', '機能説明')}</p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: #f9fafb;
                padding: 60px 40px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h2 {{
                font-size: 2.5rem;
                font-weight: 800;
                color: #1f2937;
                text-align: center;
                margin-bottom: 16px;
            }}
            .intro {{
                text-align: center;
                color: #6b7280;
                font-size: 1.1rem;
                margin-bottom: 48px;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 32px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{section_title}</h2>
            <div class="intro">{introduction}</div>
            <div class="features-grid">
                {features_html}
            </div>
        </div>
    </body>
    </html>
    """

def generate_testimonials_preview(template):
    """テスティモニアルのプレビュー生成"""
    section_title = template.get('section_title', 'お客様の声')
    testimonials = template.get('testimonials', [])
    
    testimonials_html = ""
    for testimonial in testimonials:
        testimonials_html += f"""
        <div style='background: white; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            <p style='color: #1f2937; font-size: 1.1rem; line-height: 1.8; margin-bottom: 24px; font-style: italic;'>
                "{testimonial.get('quote', 'コメント')}"
            </p>
            <div style='border-top: 2px solid #e5e7eb; padding-top: 16px;'>
                <div style='font-weight: 700; color: #1f2937; margin-bottom: 4px;'>{testimonial.get('author', '名前')}</div>
                <div style='color: #6b7280; font-size: 0.9rem;'>{testimonial.get('position', '役職')} - {testimonial.get('company', '企業名')}</div>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: #f9fafb;
                padding: 60px 40px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h2 {{
                font-size: 2.5rem;
                font-weight: 800;
                color: #1f2937;
                text-align: center;
                margin-bottom: 48px;
            }}
            .testimonials-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 32px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{section_title}</h2>
            <div class="testimonials-grid">
                {testimonials_html}
            </div>
        </div>
    </body>
    </html>
    """

def generate_social_proof_preview(template):
    """導入企業のプレビュー生成"""
    section_title = template.get('section_title', '導入企業')
    companies = template.get('companies', [])
    stats = template.get('stats', {})
    
    companies_html = ""
    for company in companies:
        companies_html += f"""
        <div style='background: white; border-radius: 8px; padding: 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
            <span style='font-weight: 600; color: #6b7280;'>{company}</span>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: #f9fafb;
                padding: 60px 40px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h2 {{
                font-size: 2.5rem;
                font-weight: 800;
                color: #1f2937;
                text-align: center;
                margin-bottom: 48px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 32px;
                margin-bottom: 48px;
            }}
            .stat-item {{
                text-align: center;
            }}
            .stat-value {{
                font-size: 3rem;
                font-weight: 800;
                color: #667eea;
                margin-bottom: 8px;
            }}
            .stat-label {{
                color: #6b7280;
                font-size: 1rem;
            }}
            .companies-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{section_title}</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{stats.get('total_companies', '1,000')}</div>
                    <div class="stat-label">導入企業数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats.get('satisfaction_rate', '98')}%</div>
                    <div class="stat-label">顧客満足度</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats.get('active_users', '50,000')}</div>
                    <div class="stat-label">アクティブユーザー</div>
                </div>
            </div>
            <div class="companies-grid">
                {companies_html}
            </div>
        </div>
    </body>
    </html>
    """

def generate_faq_preview(template):
    """FAQのプレビュー生成"""
    section_title = template.get('section_title', 'よくある質問')
    questions = template.get('questions', [])
    
    faq_html = ""
    for i, faq in enumerate(questions):
        faq_html += f"""
        <div style='border-bottom: 1px solid #e5e7eb; padding: 24px 0;'>
            <div style='font-weight: 700; color: #1f2937; font-size: 1.1rem; margin-bottom: 12px;'>
                Q. {faq.get('question', '質問')}
            </div>
            <div style='color: #6b7280; line-height: 1.6; padding-left: 24px;'>
                A. {faq.get('answer', '回答')}
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: #f9fafb;
                padding: 60px 40px;
            }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h2 {{
                font-size: 2.5rem;
                font-weight: 800;
                color: #1f2937;
                text-align: center;
                margin-bottom: 48px;
            }}
            .faq-container {{
                background: white;
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{section_title}</h2>
            <div class="faq-container">
                {faq_html}
            </div>
        </div>
    </body>
    </html>
    """

# ===== スマートバックアップ機能 =====

def show_smart_backup_alert(template_data):
    """新規テンプレート作成時のスマートバックアップアラート"""
    if not st.session_state.get('show_backup_alerts', True):
        return
    
    template_name = template_data.get('name', '新規テンプレート')
    
    alert_html = f"""
    <div class="backup-alert">
        <h3>🎉 テンプレート「{html.escape(template_name)}」を保存しました！</h3>
        <p style="margin-bottom: 15px; color: #e0e7ff;">💡 <strong>今すぐバックアップしませんか？</strong> 
        データが消失する前に、1クリックで安全に保存できます。</p>
        
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button onclick="copyToClipboard()" id="copyBtn" class="cyber-button">
                📋 クリップボードにコピー
            </button>
            <button onclick="downloadTemplate()" id="downloadBtn" class="cyber-button">
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
        
        backup_data = create_backup_data()
        if backup_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lp_templates_backup_{timestamp}.json"
            
            st.sidebar.download_button(
                label="💾 全テンプレートをダウンロード",
                data=backup_data,
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 設定")
    
    show_alerts = st.sidebar.checkbox(
        "バックアップアラートを表示",
        value=st.session_state.get('show_backup_alerts', True)
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
        template_data['status'] = 'draft'  # 下書き状態
        
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
    
    st.title("🔮 LP Template Manager - Cyberpunk Edition")
    st.markdown("**BtoB SaaS特化のLPテンプレート管理ツール**")
    
    with st.sidebar:
        st.markdown("## 🎛️ 操作パネル")
        
        mode = st.radio(
            "モードを選択してください",
            ["template_registration", "design_creation"],
            format_func=lambda x: "📝 テンプレート登録" if x == "template_registration" else "🎨 デザイン作成"
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
        ① 基本情報入力 → ② プロンプト生成・ChatGPTへコピー → ③ JSONデータ入力＋プレビュー → ④ 保存・管理
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Step 1: 基本情報",
        "🤖 Step 2: プロンプト生成",
        "📋 Step 3: JSONデータ＋プレビュー",
        "💾 Step 4: 保存・管理"
    ])
    
    # ===== Step 1: 基本情報 =====
    with tab1:
        st.markdown("### 📌 テンプレートの基本情報を入力")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input(
                "テンプレート名",
                placeholder="例: BtoB向けSaaSLPでかいCTA",
                key="template_name"
            )
            
            reference_url = st.text_input(
                "参考URL",
                placeholder="https://www.freee.co.jp/accounting/fr-oyj79k",
                key="reference_url"
            )
        
        with col2:
            section_type = st.selectbox(
                "セクション種別",
                list(SECTION_LABELS.keys()),
                format_func=lambda x: SECTION_LABELS[x],
                key="section_type"
            )
            
            description = st.text_area(
                "説明",
                placeholder="大きくて見やすいヘッダー",
                key="template_description",
                height=100
            )
        
        st.success("✅ 基本情報の入力が完了しました！次は「Step 2: プロンプト生成」タブへ")
    
    # ===== Step 2: プロンプト生成 =====
    with tab2:
        st.markdown("### 🤖 ChatGPTに投げるプロンプトを生成")
        
        st.markdown("""
        <div class="help-box">
            💡 <strong>このステップでやること:</strong><br>
            1. 「プロンプトを生成」ボタンをクリック<br>
            2. 生成されたプロンプトを「コピー」ボタンでコピー<br>
            3. ChatGPTに貼り付けて、JSONデータを取得<br>
            4. 取得したJSONを「Step 3」で入力
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 プロンプトを生成", key="generate_prompt", type="primary", use_container_width=True):
            template_name = st.session_state.get('template_name', 'サンプルテンプレート')
            section_type = st.session_state.get('section_type', 'hero')
            reference_url = st.session_state.get('reference_url', 'https://example.com')
            description = st.session_state.get('template_description', '説明なし')
            
            if section_type in SECTION_PROMPTS:
                prompt = SECTION_PROMPTS[section_type].format(
                    template_name=template_name,
                    reference_url=reference_url,
                    description=description
                )
                st.session_state.generated_prompt = prompt
        
        if 'generated_prompt' in st.session_state:
            st.markdown("### 📄 生成されたプロンプト")
            st.markdown(f'<div class="prompt-box">{html.escape(st.session_state.generated_prompt)}</div>', unsafe_allow_html=True)
            
            copy_js = f"""
            <button onclick="copyPrompt()" id="copyPromptBtn" class="cyber-button" style="margin-top: 12px;">
                📋 プロンプトをコピー
            </button>
            
            <script>
            function copyPrompt() {{
                const promptText = {json.dumps(st.session_state.generated_prompt)};
                
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(promptText).then(function() {{
                        document.getElementById('copyPromptBtn').innerHTML = '✅ コピーしました！';
                        setTimeout(() => {{
                            document.getElementById('copyPromptBtn').innerHTML = '📋 プロンプトをコピー';
                        }}, 3000);
                    }});
                }}
            }}
            </script>
            """
            st.markdown(copy_js, unsafe_allow_html=True)
            
            st.success("✅ ChatGPTに貼り付けて、JSONを取得してください！")
    
    # ===== Step 3: JSONデータ＋プレビュー =====
    with tab3:
        st.markdown("### 📋 ChatGPTから取得したJSONデータを入力")
        
        json_input = st.text_area(
            "JSONデータ",
            placeholder='{"title": "タイトル", "subtitle": "サブタイトル", ...}',
            height=250,
            key="json_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 JSONをパース＋プレビュー", key="parse_json", type="primary", use_container_width=True):
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
                        st.success("✅ JSONをパースしました！")
                    else:
                        st.error("❌ JSONデータを入力してください")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON解析エラー: {str(e)}")
                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")
        
        with col2:
            if st.button("🔄 入力をクリア", key="clear_json", use_container_width=True):
                st.session_state.json_input = ""
                if 'temp_template' in st.session_state:
                    del st.session_state.temp_template
                st.rerun()
        
        # プレビュー表示
        if 'temp_template' in st.session_state:
            st.markdown("---")
            st.markdown("### 👀 プレビュー")
            
            try:
                preview_html = generate_section_preview(st.session_state.temp_template)
                st.components.v1.html(preview_html, height=600, scrolling=True)
            except Exception as e:
                st.error(f"プレビュー生成エラー: {str(e)}")
            
            st.markdown("### 📄 JSONデータ")
            st.json(st.session_state.temp_template)
            
            st.success("✅ プレビュー確認OK！「Step 4」で保存してください。")
    
    # ===== Step 4: 保存・管理 =====
    with tab4:
        st.markdown("### 💾 テンプレートの保存・管理")
        
        col1, col2 = st.columns(2)
        
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
                status = template.get('status', 'draft')
                status_emoji = "📝" if status == "draft" else "✅"
                
                with st.expander(f"{status_emoji} {template.get('name', '無名')} - {SECTION_LABELS.get(template.get('section_type', 'unknown'), '不明')}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**作成:** {template.get('created_at', 'N/A')[:19]}")
                        st.write(f"**状態:** {status}")
                    
                    with col2:
                        if st.button("👁️ プレビュー", key=f"preview_{template_id}", use_container_width=True):
                            st.session_state.preview_template = template
                    
                    with col3:
                        if st.button("🎨 編集", key=f"edit_{template_id}", use_container_width=True):
                            st.session_state.selected_template = template_id
                            st.session_state.current_mode = "design_creation"
                            st.rerun()
                    
                    with col4:
                        if st.button("🗑️ 削除", key=f"delete_{template_id}", use_container_width=True):
                            del st.session_state.templates[template_id]
                            st.success("✅ 削除しました")
                            st.rerun()
                    
                    # 承認ボタン（下書きの場合のみ）
                    if status == 'draft':
                        if st.button("✅ 承認", key=f"approve_{template_id}", use_container_width=True):
                            st.session_state.templates[template_id]['status'] = 'approved'
                            st.success("✅ テンプレートを承認しました")
                            st.rerun()
                    
                    # プレビュー表示
                    if st.session_state.get('preview_template', {}).get('id') == template_id:
                        st.markdown("---")
                        st.markdown("#### プレビュー")
                        try:
                            preview_html = generate_section_preview(template)
                            st.components.v1.html(preview_html, height=500, scrolling=True)
                        except Exception as e:
                            st.error(f"プレビューエラー: {str(e)}")
                    
                    # JSONデータ表示
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
