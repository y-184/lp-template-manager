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

# ===== シンプル＆確実スタイル =====

st.markdown("""
<style>
    /* 基本設定：白背景 + 黒文字 */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* ヘルプボックス */
    .help-box {
        background-color: #f0f4ff;
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        color: #1e293b;
    }
    
    .help-box strong {
        color: #1e40af;
    }
    
    /* プロンプトボックス */
    .prompt-box {
        background-color: #f9fafb;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #111827;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* バックアップアラート */
    .backup-alert {
        background-color: #ecfdf5;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        color: #065f46;
    }
    
    .backup-alert h3 {
        color: #047857;
        margin-bottom: 12px;
        font-size: 18px;
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
    """
    freee風の詳細JSON構造に完全対応したヒーローセクションプレビュー生成
    
    対応形式：
    1. 詳細形式: content, layout, background キーを持つ構造
    2. シンプル形式: title, layout, background などのフラット構造
    3. レガシー形式: title, subtitle, description のみ
    """
    
    # === 形式判定 ===
    has_content_key = 'content' in template
    has_layout_key = 'layout' in template and isinstance(template.get('layout'), (dict, str))
    has_background_key = 'background' in template
    has_simple_keys = 'title' in template or 'title_size' in template
    
    # 新形式（詳細 or シンプル）の判定
    is_advanced_format = has_content_key or (has_simple_keys and (has_layout_key or has_background_key))
    
    if is_advanced_format:
        # === 新形式: 詳細 or シンプル ===
        
        # 詳細形式の場合
        if has_content_key:
            content = template.get('content', {})
            main_title_data = content.get('main_title', {})
            title_text = main_title_data.get('example', 'タイトル')
            title_font_size = main_title_data.get('font_size', '56px')
            title_color = main_title_data.get('color', '#333333')
            title_line_height = main_title_data.get('line_height', '1.4')
            
            # 変数置換
            variables = template.get('variables', {})
            for key, value in variables.items():
                title_text = title_text.replace(f'{{{{{key}}}}}', value)
            
            subtitle_data = content.get('subtitle', {})
            subtitle_text = subtitle_data.get('example', '')
            subtitle_font_size = subtitle_data.get('font_size', '18px')
            subtitle_color = subtitle_data.get('color', '#666666')
            subtitle_line_height = subtitle_data.get('line_height', '1.8')
            subtitle_max_width = subtitle_data.get('max_width', '600px')
            
            for key, value in variables.items():
                subtitle_text = subtitle_text.replace(f'{{{{{key}}}}}', value)
            
            # CTA生成
            cta_section = content.get('cta_section', {})
            buttons = cta_section.get('buttons', [])
            cta_gap = cta_section.get('gap', '16px')
            
            cta_html = ""
            if buttons:
                btn_items = []
                for btn in buttons:
                    label_above = btn.get('label_above', {})
                    label_html = ""
                    if label_above:
                        label_html = f"<div style='font-size: {label_above.get('font_size', '12px')}; color: {label_above.get('color', '#666')}; margin-bottom: 8px;'>{label_above.get('text', '')}</div>"
                    
                    btn_items.append(f"""
                    <div style='display: flex; flex-direction: column; align-items: flex-start;'>
                        {label_html}
                        <button style='width: {btn.get('width', '240px')}; height: {btn.get('height', '64px')}; 
                                        font-size: {btn.get('font_size', '18px')}; font-weight: bold; 
                                        background: {btn.get('background', '#0066FF')}; color: {btn.get('color', '#FFF')}; 
                                        border: {btn.get('border', 'none')}; border-radius: {btn.get('border_radius', '32px')}; 
                                        cursor: pointer;'>{btn.get('text', 'ボタン')}</button>
                    </div>
                    """)
                cta_html = f"<div style='display: flex; gap: {cta_gap}; margin-bottom: 40px; flex-wrap: wrap;'>{''.join(btn_items)}</div>"
            
            # Trust Badges生成
            trust_badges_data = content.get('trust_badges', {})
            trust_items = trust_badges_data.get('items', [])
            trust_html = ""
            if trust_items:
                badge_list = []
                for item in trust_items:
                    text_display = item.get('text_example', '').replace('\n', '<br>')
                    badge_list.append(f"""
                    <div style='width: {item.get('width', '180px')}; height: {item.get('height', '120px')}; 
                                background: {item.get('background', '#F8F9FA')}; border-radius: {item.get('border_radius', '12px')}; 
                                padding: {item.get('padding', '16px')}; display: flex; flex-direction: column; 
                                align-items: center; justify-content: center; text-align: center; 
                                font-size: {item.get('font_size', '14px')}; font-weight: bold;'>{text_display}</div>
                    """)
                trust_html = f"<div style='display: flex; gap: {trust_badges_data.get('gap', '32px')}; flex-wrap: wrap;'>{''.join(badge_list)}</div>"
            
            layout_obj = template.get('layout', {})
            layout_structure = layout_obj.get('structure', 'center')
            left_column = layout_obj.get('left_column', {})
            left_width = left_column.get('width', '45%')
            left_padding = left_column.get('padding', '80px 60px')
            left_alignment = left_column.get('alignment', 'left')
            
            right_column = layout_obj.get('right_column', {})
            right_width = right_column.get('width', '55%')
            
            background_obj = template.get('background', {})
            bg_colors = background_obj.get('colors', [
                {"position": "0%", "color": "#E3F2FD"},
                {"position": "50%", "color": "#F5F5FF"},
                {"position": "100%", "color": "#FFFFFF"}
            ])
            gradient_stops = ', '.join([f"{c['color']} {c['position']}" for c in bg_colors])
            bg_gradient = f"linear-gradient(135deg, {gradient_stops})"
            
        else:
            # シンプル形式
            title_text = template.get('title', 'タイトル')
            title_font_size = template.get('title_size', '56px')
            title_color = template.get('title_color', '#333333')
            title_line_height = '1.4'
            
            subtitle_text = template.get('subtitle', '')
            subtitle_font_size = template.get('subtitle_size', '18px')
            subtitle_color = template.get('subtitle_color', '#666666')
            subtitle_line_height = '1.8'
            subtitle_max_width = '600px'
            
            # CTA生成（シンプル形式）
            cta_primary_text = template.get('cta_primary_text', '無料で始める')
            cta_primary_bg = template.get('cta_primary_bg', '#0066FF')
            cta_secondary_text = template.get('cta_secondary_text', '資料請求')
            
            cta_html = f"""
            <div style='display: flex; gap: 16px; margin-bottom: 40px; flex-wrap: wrap;'>
                <button style='width: 240px; height: 64px; font-size: 18px; font-weight: bold; 
                                background: {cta_primary_bg}; color: #FFFFFF; border: none; 
                                border-radius: 32px; cursor: pointer;'>{cta_primary_text}</button>
                <button style='width: 240px; height: 64px; font-size: 18px; font-weight: bold; 
                                background: transparent; color: {cta_primary_bg}; border: 2px solid {cta_primary_bg}; 
                                border-radius: 32px; cursor: pointer;'>{cta_secondary_text}</button>
            </div>
            """
            
            # Trust Badges（シンプル形式）
            trust_badge_1 = template.get('trust_badge_1', '')
            trust_badge_2 = template.get('trust_badge_2', '')
            trust_html = ""
            if trust_badge_1 or trust_badge_2:
                badges = []
                if trust_badge_1:
                    badges.append(f"<div style='width: 180px; height: 120px; background: #F8F9FA; border-radius: 12px; padding: 16px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 14px; font-weight: bold;'>{trust_badge_1}</div>")
                if trust_badge_2:
                    badges.append(f"<div style='width: 180px; height: 120px; background: #F8F9FA; border-radius: 12px; padding: 16px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 14px; font-weight: bold;'>{trust_badge_2}</div>")
                trust_html = f"<div style='display: flex; gap: 32px; flex-wrap: wrap;'>{''.join(badges)}</div>"
            
            # レイアウト判定
            layout_value = template.get('layout', '')
            if layout_value == 'left_right_split' or layout_value == 'two_column_split':
                layout_structure = 'two_column_split'
            else:
                layout_structure = 'center'
            
            left_width = '45%'
            left_padding = '80px 60px'
            left_alignment = 'left'
            right_width = '55%'
            
            # 背景
            bg_value = template.get('background', '')
            if bg_value and 'linear-gradient' in bg_value:
                bg_gradient = bg_value
            else:
                bg_gradient = "linear-gradient(135deg, #E3F2FD 0%, #F5F5FF 50%, #FFFFFF 100%)"
        
        # HTML生成（左右分割レイアウト）
        if layout_structure == 'two_column_split':
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Inter', sans-serif; background: {bg_gradient}; min-height: 100vh; }}
                    .hero-container {{ display: flex; min-height: 100vh; align-items: center; }}
                    .left-column {{ width: {left_width}; padding: {left_padding}; text-align: {left_alignment}; }}
                    .right-column {{ width: {right_width}; display: flex; align-items: center; justify-content: center; padding: 40px; }}
                    .main-title {{ font-size: {title_font_size}; font-weight: bold; color: {title_color}; 
                                   line-height: {title_line_height}; margin-bottom: 32px; white-space: pre-line; }}
                    .subtitle {{ font-size: {subtitle_font_size}; color: {subtitle_color}; line-height: {subtitle_line_height}; 
                                 max-width: {subtitle_max_width}; margin-bottom: 48px; }}
                    .right-visual {{ width: 600px; height: 400px; background: rgba(255, 255, 255, 0.5); 
                                     border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                                     color: #999; font-size: 16px; border: 2px dashed #ccc; }}
                </style>
            </head>
            <body>
                <div class="hero-container">
                    <div class="left-column">
                        <h1 class="main-title">{title_text}</h1>
                        <div class="subtitle">{subtitle_text}</div>
                        {cta_html}
                        {trust_html}
                    </div>
                    <div class="right-column">
                        <div class="right-visual">プロダクト画像エリア</div>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # === レガシー形式: シンプル構造（後方互換性） ===
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
    
    # レガシー形式のデフォルト背景（グレー）
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
                background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px;
            }}
            .container {{
                max-width: 1200px;
                text-align: center;
                color: #333;
            }}
            h1 {{
                font-size: clamp(2rem, 5vw, 4rem);
                font-weight: 800;
                margin-bottom: 24px;
                line-height: 1.2;
                color: #1a202c;
            }}
            .subtitle {{
                font-size: clamp(1rem, 2vw, 1.5rem);
                color: #4a5568;
                margin-bottom: 16px;
                font-weight: 500;
            }}
            .description {{
                font-size: 1.1rem;
                color: #718096;
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
                background: #3b82f6;
                color: white;
                padding: 16px 48px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 1.1rem;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }}
            .cta-secondary {{
                background: transparent;
                color: #3b82f6;
                padding: 16px 48px;
                border-radius: 12px;
                font-weight: 700;
                font-size: 1.1rem;
                border: 2px solid #3b82f6;
                cursor: pointer;
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
