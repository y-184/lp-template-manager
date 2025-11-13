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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    .stApp {
        background-color: #F9FAFB;
    }
    iframe {
        width: 100% !important;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===== BtoB SaaS特化セクション定義 =====

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

# ===== JSON抽出ユーティリティ関数 =====

def safe_get_nested(data, path, default=None):
    """
    ネストされたJSONから値を安全に取得
    例: safe_get_nested(data, "content.title", "デフォルト値")
    """
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

def extract_features_data(template):
    """機能紹介セクション用データ抽出"""
    content = template.get('content', {})
    
    title = safe_get_nested(content, 'title', '主要機能')
    subtitle = safe_get_nested(content, 'subtitle', '')
    
    # 機能リスト抽出 - feature_categoriesまたはfeaturesに対応
    features = []
    
    # 詳細構造: feature_categories
    feature_categories = safe_get_nested(content, 'feature_categories', [])
    if isinstance(feature_categories, list):
        for category in feature_categories:
            if isinstance(category, dict):
                category_features = category.get('features', [])
                if isinstance(category_features, list):
                    for feature in category_features:
                        if isinstance(feature, dict):
                            name = feature.get('feature_name', '')
                            desc = feature.get('feature_description', '')
                            benefit = feature.get('benefit', '')
                            if name:
                                features.append({
                                    'name': name, 
                                    'description': desc,
                                    'benefit': benefit
                                })
    
    # シンプル構造: features
    if not features:
        simple_features = safe_get_nested(content, 'features', [])
        if isinstance(simple_features, list):
            for feature in simple_features:
                if isinstance(feature, str):
                    features.append({'name': feature, 'description': '', 'benefit': ''})
                elif isinstance(feature, dict):
                    features.append({
                        'name': feature.get('name', feature.get('feature_name', '')),
                        'description': feature.get('description', feature.get('feature_description', '')),
                        'benefit': feature.get('benefit', '')
                    })
    
    return {
        'title': title,
        'subtitle': subtitle,
        'features': features
    }

def extract_testimonials_data(template):
    """お客様の声セクション用データ抽出"""
    content = template.get('content', {})
    
    title = safe_get_nested(content, 'title', 'お客様の声')
    subtitle = safe_get_nested(content, 'subtitle', '')
    
    # 証言抽出
    testimonials = []
    raw_testimonials = safe_get_nested(content, 'testimonials', [])
    
    if isinstance(raw_testimonials, list):
        for testimonial in raw_testimonials:
            if isinstance(testimonial, dict):
                testimonials.append({
                    'name': testimonial.get('customer_name', '【お客様名】'),
                    'title': testimonial.get('customer_title', ''),
                    'company': testimonial.get('company_name', '【企業名】'),
                    'text': testimonial.get('testimonial_text', ''),
                    'rating': testimonial.get('rating', 5),
                    'achievement': testimonial.get('key_achievement', '')
                })
    
    # デフォルトデータ
    if not testimonials:
        testimonials = [
            {
                'name': '【お客様A】',
                'title': '【役職】',
                'company': '【A社】',
                'text': '導入により業務効率が大幅に向上しました。直感的な操作で、チーム全体がすぐに使いこなせるようになりました。',
                'rating': 5,
                'achievement': '業務効率40%向上'
            },
            {
                'name': '【お客様B】',
                'title': '【役職】', 
                'company': '【B社】',
                'text': '以前は手作業で時間がかかっていた作業が、自動化により大幅に短縮されました。ROIも期待以上です。',
                'rating': 5,
                'achievement': '作業時間50%削減'
            },
            {
                'name': '【お客様C】',
                'title': '【役職】',
                'company': '【C社】',
                'text': 'サポート体制も充実しており、導入から運用まで安心して進められました。',
                'rating': 5,
                'achievement': '導入コスト30%削減'
            }
        ]
    
    return {
        'title': title,
        'subtitle': subtitle,
        'testimonials': testimonials
    }

# ===== セッションステート初期化 =====

def init_session_state():
    """セッションステートを初期化"""
    if "templates" not in st.session_state:
        # BtoB SaaS特化のサンプルデータ
        st.session_state.templates = [
            # ヒーローセクション サンプル
            {
                "template_id": "hero_saas_001",
                "display_name": "BtoB SaaS向けヒーローセクション",
                "section_type": "hero",
                "status": "approved",
                "metadata": {
                    "source_url": "https://example.com",
                    "description": "インパクトのあるメイン画像とキャッチコピーでファーストビューを最適化",
                    "screenshot_url": "",
                    "tags": ["BtoB", "SaaS", "ヒーロー"],
                    "created_by": "system",
                    "created_at": "2025-01-13",
                    "updated_at": "2025-01-13",
                    "review_comment": ""
                },
                "layout": {
                    "alignment": "center",
                    "background_color": "#F8FAFC"
                },
                "content": {
                    "title": "【業務効率化】を、\n【誰でも】、\n【簡単に】。",
                    "subtitle": "【サービス名】で、【業務A】から【業務B】まで一元管理。【対象ユーザー】の生産性を【効果】倍に向上させます。",
                    "bullets": [],
                    "cta_label": "無料トライアルを開始",
                    "features": ["【機能A】", "【機能B】", "【機能C】"]
                }
            },
            # 機能紹介 サンプル
            {
                "template_id": "features_saas_001", 
                "display_name": "SaaS機能紹介（3カラム）",
                "section_type": "features",
                "status": "approved",
                "metadata": {
                    "source_url": "https://example.com",
                    "description": "主要機能を3つのカラムで視覚的に紹介",
                    "screenshot_url": "",
                    "tags": ["BtoB", "SaaS", "機能"],
                    "created_by": "system",
                    "created_at": "2025-01-13", 
                    "updated_at": "2025-01-13",
                    "review_comment": ""
                },
                "layout": {
                    "alignment": "center",
                    "background_color": "#FFFFFF"
                },
                "content": {
                    "title": "【サービス名】の主要機能",
                    "subtitle": "【業務効率化】に必要な機能がすべて揃っています",
                    "features": [
                        {
                            "icon": "📊",
                            "title": "【機能A】",
                            "description": "【機能Aの詳細説明】により、【効果A】を実現します。"
                        },
                        {
                            "icon": "🔄",
                            "title": "【機能B】", 
                            "description": "【機能Bの詳細説明】で、【効果B】が可能になります。"
                        },
                        {
                            "icon": "📈",
                            "title": "【機能C】",
                            "description": "【機能Cの詳細説明】により、【効果C】を達成できます。"
                        }
                    ],
                    "bullets": [],
                    "cta_label": ""
                }
            },
            # お客様の声 サンプル
            {
                "template_id": "testimonials_saas_001",
                "display_name": "お客様の声（3名）",
                "section_type": "testimonials", 
                "status": "approved",
                "metadata": {
                    "source_url": "https://example.com",
                    "description": "信頼性向上のためのお客様の声を3名分表示",
                    "screenshot_url": "",
                    "tags": ["BtoB", "SaaS", "実績"],
                    "created_by": "system",
                    "created_at": "2025-01-13",
                    "updated_at": "2025-01-13", 
                    "review_comment": ""
                },
                "layout": {
                    "alignment": "center",
                    "background_color": "#F9FAFB"
                },
                "content": {
                    "title": "お客様の声",
                    "subtitle": "【サービス名】をご利用いただいているお客様からの声をご紹介します",
                    "testimonials": [
                        {
                            "name": "【お客様A名】",
                            "company": "【A社】【役職】",
                            "comment": "【サービス名】導入により、【具体的効果】を実現できました。特に【機能】が優秀で、【業務改善結果】につながっています。",
                            "rating": 5,
                            "avatar": "👨‍💼"
                        },
                        {
                            "name": "【お客様B名】", 
                            "company": "【B社】【役職】",
                            "comment": "以前は【課題】に困っていましたが、【サービス名】で【解決結果】。ROIは【数値】％向上しました。",
                            "rating": 5,
                            "avatar": "👩‍💼"
                        },
                        {
                            "name": "【お客様C名】",
                            "company": "【C社】【役職】", 
                            "comment": "操作が【使いやすさ】で、【導入期間】で全社展開完了。【定量的効果】の成果が出ています。",
                            "rating": 5,
                            "avatar": "👨‍💻"
                        }
                    ],
                    "bullets": [],
                    "cta_label": ""
                }
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

# ===== セクション別プレビュー生成関数 =====

def generate_section_preview(template, brand_color="#2563EB"):
    """セクション別の最適化されたプレビュー生成"""
    section_type = template.get("section_type", "")
    
    if section_type == "hero":
        return generate_hero_preview(template, brand_color)
    elif section_type == "features":
        return generate_features_preview(template, brand_color)
    elif section_type == "testimonials":
        return generate_testimonials_preview(template, brand_color)
    elif section_type == "how_it_works":
        return generate_how_it_works_preview(template, brand_color)
    elif section_type == "social_proof":
        return generate_social_proof_preview(template, brand_color)
    elif section_type == "faq":
        return generate_faq_preview(template, brand_color)
    else:
        # 従来のセクション（trouble, pricing, cta等）
        return generate_ultra_preview(template, brand_color)

def generate_hero_preview(template, brand_color="#2563EB"):
    """ヒーローセクション専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#F8FAFC'))
    
    content = template.get('content', {})
    
    # タイトル取得（\nを<br>に変換）
    title = content.get('title', '').replace('\\n', '<br>').replace('\n', '<br>')
    subtitle = content.get('subtitle', '')
    
    # CTA取得 - cta_buttonsとcta_label両方に対応
    cta_label = ''
    cta_buttons = content.get('cta_buttons', [])
    if isinstance(cta_buttons, list) and len(cta_buttons) > 0:
        # primary typeのボタンを探す
        primary_cta = next((btn for btn in cta_buttons if isinstance(btn, dict) and btn.get('type') == 'primary'), None)
        if primary_cta:
            cta_label = primary_cta.get('label', '')
    
    # 従来のcta_labelもサポート
    if not cta_label:
        cta_label = content.get('cta_label', '')
    
    # Features取得 - trust_badgesとfeatures両方に対応
    features = []
    
    # trust_badgesから取得
    trust_badges = content.get('trust_badges', [])
    if isinstance(trust_badges, list):
        for badge in trust_badges:
            if isinstance(badge, dict):
                primary_text = badge.get('primary_text', '').replace('\n', ' ').replace('\\n', ' ')
                highlight = badge.get('highlight', '')
                if primary_text and highlight:
                    features.append(f"{primary_text} {highlight}")
    
    # 従来のfeaturesもサポート
    if not features:
        features = content.get('features', [])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .hero-section {{
                background: linear-gradient(135deg, {bg_color} 0%, {primary_color}10 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                padding: 100px 40px;
                position: relative;
                overflow: hidden;
            }}
            
            .hero-container {{
                max-width: 1400px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 80px;
                align-items: center;
            }}
            
            .hero-content {{
                z-index: 10;
            }}
            
            .hero-title {{
                font-size: clamp(2.5rem, 6vw, 4.5rem);
                font-weight: 800;
                color: #1F2937;
                margin-bottom: 32px;
                line-height: 1.1;
                letter-spacing: -0.02em;
            }}
            
            .title-highlight {{
                background: linear-gradient(135deg, {primary_color}, #F59E0B);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .hero-subtitle {{
                font-size: 1.25rem;
                color: #6B7280;
                margin-bottom: 40px;
                line-height: 1.7;
            }}
            
            .hero-features {{
                display: flex;
                gap: 24px;
                margin-bottom: 48px;
                flex-wrap: wrap;
            }}
            
            .feature-badge {{
                background: rgba(255, 255, 255, 0.9);
                padding: 12px 20px;
                border-radius: 25px;
                border: 1px solid {primary_color}30;
                color: {primary_color};
                font-weight: 600;
                font-size: 0.9rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            .hero-cta {{
                background: linear-gradient(135deg, {primary_color} 0%, #F59E0B 100%);
                color: white;
                padding: 18px 48px;
                border-radius: 50px;
                border: none;
                font-size: 1.2rem;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 8px 24px {primary_color}40;
                transition: all 0.3s ease;
            }}
            
            .hero-cta:hover {{
                transform: translateY(-2px);
                box-shadow: 0 12px 32px {primary_color}50;
            }}
            
            .hero-visual {{
                background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 400px;
            }}
            
            .placeholder-visual {{
                font-size: 4rem;
                color: {primary_color};
                text-align: center;
            }}
            
            @media (max-width: 768px) {{
                .hero-container {{
                    grid-template-columns: 1fr;
                    gap: 40px;
                    text-align: center;
                }}
                .hero-section {{
                    padding: 60px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="hero-section">
            <div class="hero-container">
                <div class="hero-content">
                    <h1 class="hero-title">
                        <span class="title-highlight">{title}</span>
                    </h1>
                    <p class="hero-subtitle">{subtitle}</p>
                    
                    {'<div class="hero-features">' + ''.join([f'<div class="feature-badge">{feature}</div>' for feature in features]) + '</div>' if features else ''}
                    
                    {f'<button class="hero-cta">{cta_label}</button>' if cta_label else ''}
                </div>
                <div class="hero-visual">
                    <div class="placeholder-visual">
                        📊💻📈<br>
                        <small style="font-size: 1.2rem; color: #6B7280;">Dashboard Image</small>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_features_preview(template, brand_color="#2563EB"):
    """機能紹介セクション専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#FFFFFF'))
    
    # 詳細JSON対応のデータ抽出
    extracted = extract_features_data(template)
    title = extracted['title']
    subtitle = extracted['subtitle']
    features = extracted['features']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .features-section {{
                background: {bg_color};
                padding: 100px 40px;
            }}
            
            .features-container {{
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }}
            
            .features-title {{
                font-size: clamp(2rem, 5vw, 3rem);
                font-weight: 700;
                color: #1F2937;
                margin-bottom: 24px;
            }}
            
            .features-subtitle {{
                font-size: 1.25rem;
                color: #6B7280;
                margin-bottom: 80px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 40px;
                margin-bottom: 60px;
            }}
            
            .feature-card {{
                background: white;
                padding: 48px 32px;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .feature-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, {primary_color}, #F59E0B);
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }}
            
            .feature-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            }}
            
            .feature-card:hover::before {{
                transform: scaleX(1);
            }}
            
            .feature-icon {{
                font-size: 3rem;
                margin-bottom: 24px;
                display: block;
            }}
            
            .feature-title {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .feature-description {{
                color: #6B7280;
                line-height: 1.6;
                font-size: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="features-section">
            <div class="features-container">
                <h2 class="features-title">{title}</h2>
                <p class="features-subtitle">{subtitle}</p>
                
                <div class="features-grid">
    """
    
    for feature in features:
        if isinstance(feature, dict):
            icon = feature.get('icon', '🔧')
            f_title = feature.get('name', feature.get('title', ''))
            description = feature.get('description', '')
            benefit = feature.get('benefit', '')
        else:
            icon = '🔧'
            f_title = str(feature)
            description = f'{feature}の詳細説明がここに入ります。'
            benefit = ''
        
        html += f"""
                    <div class="feature-card">
                        <span class="feature-icon">{icon}</span>
                        <h3 class="feature-title">{f_title}</h3>
                        <p class="feature-description">{description}</p>
                        {f'<p class="feature-benefit" style="color: {primary_color}; font-weight: 600; font-size: 0.9rem; margin-top: 12px;">✓ {benefit}</p>' if benefit else ''}
                    </div>
        """
    
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_testimonials_preview(template, brand_color="#2563EB"):
    """お客様の声専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#F9FAFB'))
    
    # 詳細JSON対応のデータ抽出
    extracted = extract_testimonials_data(template)
    title = extracted['title']
    subtitle = extracted['subtitle']
    testimonials = extracted['testimonials']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .testimonials-section {{
                background: {bg_color};
                padding: 100px 40px;
            }}
            
            .testimonials-container {{
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }}
            
            .testimonials-title {{
                font-size: clamp(2rem, 5vw, 3rem);
                font-weight: 700;
                color: #1F2937;
                margin-bottom: 24px;
            }}
            
            .testimonials-subtitle {{
                font-size: 1.25rem;
                color: #6B7280;
                margin-bottom: 80px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .testimonials-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 32px;
            }}
            
            .testimonial-card {{
                background: white;
                padding: 40px 32px;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                text-align: left;
                position: relative;
            }}
            
            .testimonial-card::before {{
                content: '"';
                position: absolute;
                top: 20px;
                right: 32px;
                font-size: 4rem;
                color: {primary_color}20;
                font-family: serif;
                line-height: 1;
            }}
            
            .testimonial-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            }}
            
            .testimonial-rating {{
                display: flex;
                gap: 4px;
                margin-bottom: 20px;
            }}
            
            .star {{
                color: #F59E0B;
                font-size: 1.2rem;
            }}
            
            .testimonial-comment {{
                color: #374151;
                line-height: 1.7;
                margin-bottom: 32px;
                font-size: 1.1rem;
                font-style: italic;
            }}
            
            .testimonial-author {{
                display: flex;
                align-items: center;
                gap: 16px;
            }}
            
            .author-avatar {{
                font-size: 3rem;
                width: 60px;
                height: 60px;
                background: {primary_color}15;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .author-info {{
                flex: 1;
            }}
            
            .author-name {{
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 4px;
                font-size: 1.1rem;
            }}
            
            .author-company {{
                color: {primary_color};
                font-size: 0.9rem;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="testimonials-section">
            <div class="testimonials-container">
                <h2 class="testimonials-title">{title}</h2>
                <p class="testimonials-subtitle">{subtitle}</p>
                
                <div class="testimonials-grid">
    """
    
    for testimonial in testimonials:
        if isinstance(testimonial, dict):
            rating = testimonial.get('rating', 5)
            comment = testimonial.get('text', testimonial.get('comment', ''))
            name = testimonial.get('name', '')
            company = testimonial.get('company', '')
            title_role = testimonial.get('title', '')
            achievement = testimonial.get('achievement', '')
            avatar = testimonial.get('avatar', '👤')
        else:
            rating = 5
            comment = str(testimonial)
            name = "お客様"
            company = "導入企業"
            avatar = '👤'
        
        stars = ''.join(['★' for _ in range(rating)])
        
        html += f"""
                    <div class="testimonial-card">
                        <div class="testimonial-rating">
                            <span class="star">{stars}</span>
                        </div>
                        <p class="testimonial-comment">{comment}</p>
                        <div class="testimonial-author">
                            <div class="author-avatar">{avatar}</div>
                            <div class="author-info">
                                <div class="author-name">{name} {title_role}</div>
                                <div class="author-company">{company}</div>
                                {f'<div class="author-achievement" style="color: {primary_color}; font-size: 0.85rem; font-weight: 600; margin-top: 4px;">{achievement}</div>' if achievement else ''}
                            </div>
                        </div>
                    </div>
        """
    
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_how_it_works_preview(template, brand_color="#2563EB"):
    """利用の流れ専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#FFFFFF'))
    
    content = template.get('content', {})
    title = content.get('title', '')
    subtitle = content.get('subtitle', '')
    steps = content.get('steps', [])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .how-it-works-section {{
                background: {bg_color};
                padding: 100px 40px;
            }}
            
            .how-it-works-container {{
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
            }}
            
            .how-it-works-title {{
                font-size: clamp(2rem, 5vw, 3rem);
                font-weight: 700;
                color: #1F2937;
                margin-bottom: 24px;
            }}
            
            .how-it-works-subtitle {{
                font-size: 1.25rem;
                color: #6B7280;
                margin-bottom: 80px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .steps-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 40px;
                position: relative;
            }}
            
            .step-card {{
                background: white;
                padding: 48px 32px;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                position: relative;
            }}
            
            .step-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            }}
            
            .step-number {{
                position: absolute;
                top: -20px;
                left: 50%;
                transform: translateX(-50%);
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, {primary_color}, #F59E0B);
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.2rem;
            }}
            
            .step-icon {{
                font-size: 3rem;
                margin-bottom: 24px;
                display: block;
            }}
            
            .step-title {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 16px;
            }}
            
            .step-description {{
                color: #6B7280;
                line-height: 1.6;
                font-size: 1rem;
            }}
            
            @media (min-width: 768px) {{
                .steps-container::before {{
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 10%;
                    right: 10%;
                    height: 2px;
                    background: linear-gradient(90deg, {primary_color}, #F59E0B);
                    z-index: 1;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="how-it-works-section">
            <div class="how-it-works-container">
                <h2 class="how-it-works-title">{title}</h2>
                <p class="how-it-works-subtitle">{subtitle}</p>
                
                <div class="steps-container">
    """
    
    default_steps = [
        {"icon": "📝", "title": "【ステップ1】", "description": "【アクション1】を実行します。【詳細説明1】"},
        {"icon": "⚙️", "title": "【ステップ2】", "description": "【アクション2】により【効果2】を得られます。"},
        {"icon": "🚀", "title": "【ステップ3】", "description": "【最終結果】が完成し、すぐに【利用開始】できます。"}
    ]
    
    steps_to_show = steps if steps else default_steps
    
    for i, step in enumerate(steps_to_show, 1):
        if isinstance(step, dict):
            icon = step.get('icon', f'🔢')
            s_title = step.get('title', f'ステップ{i}')
            description = step.get('description', '')
        else:
            icon = f'🔢'
            s_title = f'ステップ{i}'
            description = str(step)
        
        html += f"""
                    <div class="step-card">
                        <div class="step-number">{i}</div>
                        <span class="step-icon">{icon}</span>
                        <h3 class="step-title">{s_title}</h3>
                        <p class="step-description">{description}</p>
                    </div>
        """
    
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_social_proof_preview(template, brand_color="#2563EB"):
    """導入企業ロゴ専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#F9FAFB'))
    
    content = template.get('content', {})
    title = content.get('title', '')
    companies = content.get('companies', [])
    
    default_companies = ["【A社】", "【B社】", "【C社】", "【D社】", "【E社】", "【F社】"]
    companies_to_show = companies if companies else default_companies
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .social-proof-section {{
                background: {bg_color};
                padding: 80px 40px;
            }}
            
            .social-proof-container {{
                max-width: 1000px;
                margin: 0 auto;
                text-align: center;
            }}
            
            .social-proof-title {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #6B7280;
                margin-bottom: 48px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            
            .companies-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 40px;
                align-items: center;
            }}
            
            .company-logo {{
                background: white;
                padding: 24px 32px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 80px;
            }}
            
            .company-logo:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            }}
            
            .company-name {{
                font-weight: 600;
                color: #374151;
                font-size: 1.1rem;
            }}
        </style>
    </head>
    <body>
        <div class="social-proof-section">
            <div class="social-proof-container">
                <h2 class="social-proof-title">{title}</h2>
                
                <div class="companies-grid">
    """
    
    for company in companies_to_show:
        company_name = company if isinstance(company, str) else company.get('name', '')
        html += f"""
                    <div class="company-logo">
                        <div class="company-name">{company_name}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_faq_preview(template, brand_color="#2563EB"):
    """FAQ専用プレビュー"""
    colors = template.get('colors', {})
    primary_color = colors.get('primary', brand_color)
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#FFFFFF'))
    
    content = template.get('content', {})
    title = content.get('title', '')
    subtitle = content.get('subtitle', '')
    faqs = content.get('faqs', [])
    
    default_faqs = [
        {"question": "【サービス名】の導入期間はどのくらいですか？", "answer": "【導入期間】で導入完了します。【サポート内容】により、スムーズな導入をサポートいたします。"},
        {"question": "料金体系について教えてください", "answer": "【料金体系説明】。詳細は料金ページをご確認いただくか、お気軽にお問い合わせください。"},
        {"question": "セキュリティ対策はどうなっていますか？", "answer": "【セキュリティ対策】を実施しており、【認証・資格】を取得しています。お客様のデータは安全に保護されます。"}
    ]
    
    faqs_to_show = faqs if faqs else default_faqs
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; }}
            
            .faq-section {{
                background: {bg_color};
                padding: 100px 40px;
            }}
            
            .faq-container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .faq-title {{
                font-size: clamp(2rem, 5vw, 3rem);
                font-weight: 700;
                color: #1F2937;
                margin-bottom: 24px;
                text-align: center;
            }}
            
            .faq-subtitle {{
                font-size: 1.25rem;
                color: #6B7280;
                margin-bottom: 60px;
                text-align: center;
            }}
            
            .faq-list {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            
            .faq-item {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border: 1px solid rgba(0,0,0,0.05);
                overflow: hidden;
                transition: all 0.3s ease;
            }}
            
            .faq-item:hover {{
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            }}
            
            .faq-question {{
                padding: 24px 32px;
                background: {primary_color}05;
                border-bottom: 1px solid {primary_color}10;
                display: flex;
                align-items: center;
                gap: 16px;
                cursor: pointer;
            }}
            
            .faq-q-label {{
                background: {primary_color};
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.9rem;
                flex-shrink: 0;
            }}
            
            .faq-q-text {{
                font-weight: 600;
                color: #1F2937;
                font-size: 1.1rem;
            }}
            
            .faq-answer {{
                padding: 24px 32px;
                background: white;
            }}
            
            .faq-a-label {{
                background: #10B981;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.9rem;
                float: left;
                margin-right: 16px;
                margin-top: 4px;
            }}
            
            .faq-a-text {{
                color: #374151;
                line-height: 1.6;
                font-size: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="faq-section">
            <div class="faq-container">
                <h2 class="faq-title">{title}</h2>
                <p class="faq-subtitle">{subtitle}</p>
                
                <div class="faq-list">
    """
    
    for faq in faqs_to_show:
        if isinstance(faq, dict):
            question = faq.get('question', '')
            answer = faq.get('answer', '')
        else:
            question = str(faq)
            answer = f'{question}に対する回答がここに表示されます。'
        
        html += f"""
                    <div class="faq-item">
                        <div class="faq-question">
                            <div class="faq-q-label">Q</div>
                            <div class="faq-q-text">{question}</div>
                        </div>
                        <div class="faq-answer">
                            <div class="faq-a-label">A</div>
                            <div class="faq-a-text">{answer}</div>
                        </div>
                    </div>
        """
    
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_ultra_preview(template, brand_color="#2563EB"):
    """従来セクション用のプレビュー（trouble, pricing, cta等）"""
    # 既存のgenerate_ultra_previewをそのまま使用
    colors = template.get('colors', {})
    typography = template.get('typography', {})
    layout_details = template.get('layout_details', {})
    visual_elements = template.get('visual_elements', {})
    
    primary_color = colors.get('primary', brand_color)
    secondary_color = colors.get('secondary', '#64748B')
    bg_color = colors.get('background', template.get('layout', {}).get('background_color', '#FFFFFF'))
    text_color = colors.get('text', '#1F2937')
    accent_color = colors.get('accent', primary_color)
    
    alignment = layout_details.get('alignment', template.get('layout', {}).get('alignment', 'center'))
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; color: {text_color}; overflow-x: hidden; }}
            
            .section-container {{
                background: {bg_color};
                min-height: 100vh;
                display: flex;
                align-items: center;
                padding: 100px 40px;
                position: relative;
                overflow: hidden;
            }}
            
            .content-wrapper {{
                max-width: 1400px;
                margin: 0 auto;
                width: 100%;
                text-align: {alignment};
                z-index: 10;
                position: relative;
            }}
            
            .title {{
                font-size: clamp(2.5rem, 8vw, 6rem);
                font-weight: 800;
                color: {text_color};
                margin-bottom: 40px;
                line-height: 1.1;
                letter-spacing: -0.02em;
                position: relative;
            }}
            
            .title-highlight {{
                background: linear-gradient(135deg, {primary_color}, {accent_color});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                position: relative;
            }}
            
            .subtitle {{
                font-size: clamp(1.125rem, 3vw, 1.5rem);
                color: {secondary_color};
                margin-bottom: 60px;
                line-height: 1.7;
                max-width: 900px;
                margin-left: auto;
                margin-right: auto;
                font-weight: 400;
            }}
            
            .cta-button {{
                background: linear-gradient(135deg, {primary_color} 0%, {accent_color} 100%);
                color: white;
                padding: 24px 60px;
                border-radius: 60px;
                border: none;
                font-size: 1.3rem;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 12px 40px {primary_color}40;
                transition: all 0.4s ease;
                text-decoration: none;
                display: inline-block;
            }}
            
            .cta-button:hover {{
                transform: translateY(-4px) scale(1.05);
                box-shadow: 0 20px 60px {primary_color}50;
            }}
        </style>
    </head>
    <body>
        <div class="section-container">
            <div class="content-wrapper">
    """
    
    # タイトル処理
    title_raw = template.get('content', {}).get('title', '')
    if title_raw:
        title_lines = title_raw.replace('\\n', '\n').split('\n')
        title_html = ""
        
        for i, line in enumerate(title_lines):
            line = line.strip()
            if line:
                if i > 0:
                    title_html += '<br>'
                title_html += line
        
        html += f'<h1 class="title"><span class="title-highlight">{title_html}</span></h1>'
    
    # サブタイトル
    subtitle = template.get('content', {}).get('subtitle', '')
    if subtitle:
        html += f'<p class="subtitle">{subtitle}</p>'
    
    # CTAボタン
    cta_label = template.get('content', {}).get('cta_label', '')
    if cta_label:
        html += f'<button class="cta-button">{cta_label}</button>'
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# ===== メインUI =====

def main():
    # タイトル
    st.markdown("""
    <div class="text-center py-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">📄 LP Template Manager</h1>
        <p class="text-xl text-gray-600">BtoB SaaS特化版 - LPのための Keynote</p>
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
        
        # セクション別統計
        templates = get_templates()
        total = len(templates)
        approved = len([t for t in templates if t["status"] == "approved"])
        
        # セクション別カウント
        section_counts = {}
        for template in templates:
            section = template.get("section_type", "unknown")
            section_counts[section] = section_counts.get(section, 0) + 1
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("総テンプレ", total)
        with col2:
            st.metric("承認済み", approved)
        
        # セクション別統計
        st.markdown("#### セクション別")
        for category, sections in SECTION_CATEGORIES.items():
            category_count = sum(section_counts.get(section, 0) for section in sections.keys())
            if category_count > 0:
                st.write(f"{category}: {category_count}件")
        
        # 新機能の説明
        st.markdown("---")
        st.info("🎯 BtoB SaaS特化版では、よく使われる10種類のセクションに対応しています！")
    
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

# ===== 各画面（BtoB SaaS特化） =====

def show_home():
    """ホーム画面（BtoB SaaS特化）"""
    st.markdown("""
    ## 👋 BtoB SaaS特化版へようこそ！
    
    **LP Template Manager v5** では、BtoB SaaSでよく使われるセクションを10種類搭載しました。
    
    ### 🎯 対応セクション
    """)
    
    # セクション一覧をカテゴリ別に表示
    for category, sections in SECTION_CATEGORIES.items():
        st.markdown(f"#### {category}")
        
        cols = st.columns(len(sections))
        for i, (section_key, section_name) in enumerate(sections.items()):
            with cols[i]:
                # 各セクションのサンプルテンプレート数
                templates = get_templates()
                count = len([t for t in templates if t.get("section_type") == section_key])
                
                st.markdown(f"""
                <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #E5E7EB; text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #1F2937;">{section_name}</h4>
                    <p style="margin: 0; color: #6B7280; font-size: 0.9rem;">{count}件のテンプレート</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 BtoB SaaS向け最適化
    
    - **ヒーローセクション**: インパクトのあるファーストビュー
    - **機能紹介**: 3カラムでの機能訴求
    - **お客様の声**: 信頼性向上のための実績表示
    - **利用の流れ**: 3ステップでの導入イメージ
    - **導入企業**: 社会的証明のためのロゴ表示
    - **よくある質問**: コンバージョン率向上のためのQ&A
    
    ### 💡 使い方
    
    1. **📝 テンプレート登録**: 参考LPから高品質テンプレート作成
    2. **🎨 LP作成**: カテゴリ別にセクションを選択してLP構築
    3. **✏️ 微調整**: 個別セクションの詳細カスタマイズ
    """)
    
    # サンプルプレビュー
    templates = get_templates()
    if templates:
        st.markdown("---")
        st.markdown("### 🎨 セクション別プレビュー例")
        
        # ヒーローセクションのプレビュー
        hero_templates = [t for t in templates if t.get("section_type") == "hero"]
        if hero_templates:
            st.markdown("#### ヒーローセクション")
            html_preview = generate_section_preview(hero_templates[0])
            st.components.v1.html(html_preview, height=400, scrolling=True)

def show_template_registration():
    """テンプレート登録画面（BtoB SaaS特化）"""
    st.markdown("## 📝 テンプレート登録 - BtoB SaaS特化")
    st.markdown("BtoB SaaSでよく使われるセクションのテンプレートを作成します。")
    
    # タブで3ステップを分ける
    tab1, tab2, tab3 = st.tabs(["Step 1: 基本情報", "Step 2: BtoB SaaS特化プロンプト", "Step 3: JSON入力・プレビュー"])
    
    # Step 1: 基本情報入力
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 基本情報入力")
            
            display_name = st.text_input("テンプレート名", placeholder="例: SaaS向けヒーローセクション", key="reg_name")
            
            # カテゴリ別セクション選択
            st.markdown("#### セクション種別")
            selected_category = st.selectbox("カテゴリ", list(SECTION_CATEGORIES.keys()))
            section_type = st.selectbox("セクション", list(SECTION_CATEGORIES[selected_category].keys()),
                                      format_func=lambda x: SECTION_CATEGORIES[selected_category][x])
            
            source_url = st.text_input("参照URL", placeholder="https://example.com/lp", key="reg_url")
            
            description = st.text_area(
                "一言メモ",
                placeholder="このテンプレートの特徴や使いどころを記載",
                height=100,
                key="reg_desc"
            )
            
            tags_input = st.text_input("タグ（カンマ区切り）", placeholder="BtoB, SaaS, ヒーロー", key="reg_tags")
            
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
                            "screenshot_url": "",
                            "tags": tags,
                            "created_by": "user",
                            "created_at": datetime.now().strftime("%Y-%m-%d"),
                            "updated_at": datetime.now().strftime("%Y-%m-%d"),
                            "review_comment": ""
                        },
                        "layout": {
                            "alignment": "center",
                            "background_color": "#FFFFFF"
                        },
                        "content": {}
                    }
                    
                    st.success("✅ 基本情報を保存しました！「Step 2」でBtoB SaaS特化プロンプトを生成してください。")
        
        with col2:
            st.markdown("### 💡 BtoB SaaS特化のコツ")
            
            # セクション別のアドバイス
            if 'selected_category' in locals():
                section_advice = {
                    "🏠 ヘッダー・導入": "**ファーストビューで勝負**\n- 明確な価値提案\n- ターゲットの特定\n- 強力なCTA",
                    "⚡ 課題・価値提案": "**課題の共感 → 解決策提示**\n- 具体的なペイン\n- 定量的な効果\n- 機能の差別化",
                    "🏆 信頼・実績": "**信頼性の向上**\n- 具体的な数字\n- 有名企業の導入\n- リアルな声",
                    "💰 料金・申し込み": "**コンバージョン最適化**\n- 明確な料金体系\n- 不安の解消\n- 行動喚起の強化"
                }
                
                advice = section_advice.get(selected_category, "")
                if advice:
                    st.info(advice)

    # Step 2: BtoB SaaS特化プロンプト生成
    with tab2:
        st.markdown("### 🎯 BtoB SaaS特化プロンプト生成")
        
        if "draft_template" not in st.session_state:
            st.warning("⚠️ 先に「Step 1」で基本情報を入力してください")
        else:
            draft = st.session_state.draft_template
            section_type = draft.get("section_type", "")
            
            st.success(f"✅ テンプレート「{draft['display_name']}」({SECTION_LABELS.get(section_type, section_type)}) の基本情報を読み込みました")
            
            # セクション別特化プロンプト
            section_specific_prompts = {
                "hero": """
【ヒーローセクション特化指針】
- メインメッセージは3行以内の改行構成
- サブコピーでターゲットと価値提案を明確化
- 主要機能を3つのバッジで表示
- 強力なCTAでアクション誘導
- 右側にダッシュボードやプロダクト画面の配置想定
""",
                "features": """
【機能紹介特化指針】
- 3つの主要機能をカード形式で配置
- アイコン + 機能名 + 詳細説明の構成
- ホバーエフェクト付きのカードデザイン
- BtoB特有の機能（連携・セキュリティ・分析等）を想定
""",
                "testimonials": """
【お客様の声特化指針】
- 3名のお客様の声を横並び配置
- 顔写真（アバター）+ 名前 + 会社・役職
- 具体的な数値効果を含むコメント
- 5段階評価の星表示
- 業界・企業規模のバリエーション
""",
                "how_it_works": """
【利用の流れ特化指針】
- 3ステップでの導入・利用フローを表示
- ステップ番号 + アイコン + 説明の構成
- 導入から効果実感まで の一連の流れ
- BtoB特有のプロセス（導入・設定・運用・効果測定）
""",
                "social_proof": """
【導入企業特化指針】
- 6社程度の企業ロゴを横並び表示
- 業界バランス（IT・製造・金融・小売等）
- 企業規模のバリエーション
- グレースケール or カラーでの統一感
""",
                "faq": """
【FAQ特化指針】
- BtoB SaaSでよくある質問3-5件
- 導入・料金・セキュリティ・サポートを網羅
- Q&A形式でアコーディオン風の表示
- 不安解消 → コンバージョン向上を意識
"""
            }
            
            specific_guidance = section_specific_prompts.get(section_type, "")
            
            # BtoB SaaS特化プロンプト生成
            saas_prompt = f"""以下のBtoB SaaS LPの{SECTION_LABELS.get(section_type, section_type)}セクションを、激似レベルで再現するテンプレートとして構造化してJSON形式で出力してください。

【基本情報】
- テンプレート名: {draft['display_name']}
- セクション種別: {section_type} ({SECTION_LABELS.get(section_type, section_type)})
- 参照URL: {draft['metadata']['source_url']}
- 説明: {draft['metadata']['description']}

【BtoB SaaS特化指針】
🎯 **ターゲット**: BtoB企業の決裁者・利用者を想定
💼 **価値提案**: 業務効率化・コスト削減・売上向上を軸とした訴求
📊 **定量効果**: 具体的な数値・ROI・導入実績を重視
🔒 **信頼性**: セキュリティ・導入企業・サポート体制の強調

{specific_guidance}

【出力すべきJSON項目】
```json
{{
  "title": "メインコピー（BtoBらしい価値提案、\\n で改行指定）",
  "subtitle": "サブコピー（ターゲットと効果を明確化）",
  {f'"features": [{{ "icon": "📊", "title": "機能名", "description": "機能説明" }}],' if section_type == 'features' else ''}
  {f'"testimonials": [{{ "name": "【お客様名】", "company": "【会社名】【役職】", "comment": "具体的効果コメント", "rating": 5, "avatar": "👨‍💼" }}],' if section_type == 'testimonials' else ''}
  {f'"steps": [{{ "icon": "📝", "title": "【ステップ1】", "description": "アクション説明" }}],' if section_type == 'how_it_works' else ''}
  {f'"companies": ["【A社】", "【B社】", "【C社】"],' if section_type == 'social_proof' else ''}
  {f'"faqs": [{{ "question": "よくある質問", "answer": "回答内容" }}],' if section_type == 'faq' else ''}
  "colors": {{
    "primary": "メインカラー（HEX）",
    "secondary": "セカンダリカラー（HEX）",
    "background": "背景色（HEX）"
  }},
  "cta_label": "CTAボタンテキスト",
  "layout_details": {{
    "alignment": "center",
    "spacing": "BtoBらしい余白設計"
  }}
}}
```

【BtoB SaaS特有の考慮点】
1. **業界用語**: 適度な専門用語で信頼性向上
2. **決裁フロー**: 複数関係者を意識した情報設計
3. **導入プロセス**: 検討→試用→導入→効果測定の流れ
4. **競合対策**: 他社との差別化ポイントの明確化
5. **ROI訴求**: 投資対効果の定量的な表現

【ChatGPTでの使用方法】
1. このプロンプトをコピー
2. 参考LPのスクリーンショットをアップロード
3. 「このBtoB SaaS LPの{SECTION_LABELS.get(section_type, section_type)}を激似レベルで再現してJSON出力してください」と指示

【注意事項】
- 固有名詞は【変数名】で置換（著作権対応）
- BtoB SaaSらしい訴求ポイントを重視
- セクションの目的（認知・理解・信頼・行動）を明確化
- 実装可能な範囲で最高品質の再現を目指す

上記のBtoB SaaS特化JSON形式で詳細出力してください。"""
            
            st.code(saas_prompt, language="text")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📋 BtoB SaaS特化プロンプトをダウンロード",
                    data=saas_prompt,
                    file_name=f"saas_{section_type}_prompt.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("➡️ Step 3へ進む", type="primary", use_container_width=True):
                    st.info("「Step 3: JSON入力・プレビュー」タブに移動してください")

    # Step 3: JSON入力・プレビュー（BtoB SaaS特化）
    with tab3:
        st.markdown("### 🎯 JSON入力・BtoB SaaS特化プレビュー")
        
        if "draft_template" not in st.session_state:
            st.warning("⚠️ 先に「Step 1」で基本情報を入力してください")
        else:
            draft = st.session_state.draft_template
            section_type = draft.get("section_type", "")
            
            st.info(f"💡 ChatGPTから返ってきたBtoB SaaS特化JSONを貼り付けてください（{SECTION_LABELS.get(section_type, section_type)}）")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### JSON入力")
                
                json_input = st.text_area(
                    "ChatGPT出力JSON（BtoB SaaS特化版）",
                    height=500,
                    placeholder='{\n  "title": "...",\n  "features": [...],\n  "colors": {...},\n  ...\n}',
                    key="json_input_saas"
                )
                
                if st.button("🎯 BtoB SaaS特化プレビュー生成", use_container_width=True, type="primary"):
                    try:
                        # JSON解析
                        content_data = json.loads(json_input)
                        
                        # ドラフトテンプレートを詳細データで更新
                        st.session_state.draft_template.update(content_data)
                        
                        # content構造の確保
                        if "content" not in st.session_state.draft_template:
                            st.session_state.draft_template["content"] = {}
                        
                        # 基本項目の更新
                        basic_content = st.session_state.draft_template["content"]
                        basic_content.update({
                            "title": content_data.get("title", ""),
                            "subtitle": content_data.get("subtitle", ""),
                            "cta_label": content_data.get("cta_label", "")
                        })
                        
                        # セクション特有データの追加
                        section_specific_fields = {
                            "features": ["features"],
                            "testimonials": ["testimonials"],
                            "how_it_works": ["steps"],
                            "social_proof": ["companies"],
                            "faq": ["faqs"]
                        }
                        
                        if section_type in section_specific_fields:
                            for field in section_specific_fields[section_type]:
                                if field in content_data:
                                    basic_content[field] = content_data[field]
                        
                        # レイアウト情報の更新
                        if "layout" not in st.session_state.draft_template:
                            st.session_state.draft_template["layout"] = {}
                        
                        layout_info = st.session_state.draft_template["layout"]
                        layout_details = content_data.get("layout_details", {})
                        colors = content_data.get("colors", {})
                        
                        layout_info.update({
                            "alignment": layout_details.get("alignment", "center"),
                            "background_color": colors.get("background", "#FFFFFF")
                        })
                        
                        st.success("✅ BtoB SaaS特化JSONを解析しました。右側で専用プレビューを確認してください。")
                        st.session_state.show_saas_preview = True
                        st.rerun()
                        
                    except json.JSONDecodeError as e:
                        st.error(f"⚠️ JSON形式エラー: {str(e)}")
                    except Exception as e:
                        st.error(f"⚠️ エラー: {str(e)}")
            
            with col2:
                st.markdown("#### 🎯 BtoB SaaS特化プレビュー")
                
                if st.session_state.get("show_saas_preview", False):
                    # セクション別特化プレビュー表示
                    html_preview = generate_section_preview(st.session_state.draft_template)
                    st.components.v1.html(html_preview, height=800, scrolling=True)
                    
                    st.markdown("---")
                    
                    # 承認アクション
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ BtoB SaaS特化で承認登録", type="primary", use_container_width=True):
                            st.session_state.draft_template["status"] = "approved"
                            add_template(st.session_state.draft_template)
                            
                            st.success("🎉 BtoB SaaS特化テンプレートを承認・登録しました！")
                            st.balloons()
                            
                            # クリーンアップ
                            del st.session_state.draft_template
                            del st.session_state.show_saas_preview
                            st.rerun()
                    
                    with col_b:
                        if st.button("📝 下書きとして保存", use_container_width=True):
                            add_template(st.session_state.draft_template)
                            
                            st.success("💾 下書きとして保存しました。「テンプレート一覧」から編集できます。")
                            
                            # クリーンアップ
                            del st.session_state.draft_template
                            del st.session_state.show_saas_preview
                            st.rerun()
                else:
                    st.info("左側でJSONを入力して「BtoB SaaS特化プレビュー生成」ボタンを押してください")

def show_page_builder():
    """LP作成画面（BtoB SaaS特化）"""
    st.markdown("## 🎨 LP作成 - BtoB SaaS特化")
    st.markdown("カテゴリ別に整理されたテンプレートを組み合わせて、完成度の高いBtoB SaaS LPを作成します。")
    
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
            ["BtoB SaaSリード獲得", "BtoB SaaS製品紹介", "BtoB SaaS料金案内", "BtoB SaaS導入事例"]
        )
        
        target = st.text_area(
            "ターゲット",
            placeholder="例: IT部門責任者 / 既存ツールの課題を抱えている企業",
            height=80
        )
        
        tone = st.selectbox("トンマナ", ["プロフェッショナル", "フレンドリー", "テクニカル", "エモーショナル"])
        
        brand_color = st.color_picker("ブランドカラー", "#2563EB")
        
        st.markdown("---")
        st.markdown("### Step 2: カテゴリ別セクション選択")
        
        # カテゴリ別セクション選択
        sections = {}
        
        for category, section_options in SECTION_CATEGORIES.items():
            with st.expander(f"{category} ({len(section_options)}種類)", expanded=True):
                for section_type, section_name in section_options.items():
                    templates_of_type = [t for t in approved_templates if t["section_type"] == section_type]
                    
                    if templates_of_type:
                        template_options = {t["display_name"]: t for t in templates_of_type}
                        selected_name = st.selectbox(
                            f"📌 {section_name}",
                            options=["未選択"] + list(template_options.keys()),
                            key=f"select_{section_type}"
                        )
                        
                        if selected_name != "未選択":
                            sections[section_type] = template_options[selected_name]
                            
                            # 個別プレビューボタン
                            if st.button(f"👁️ {section_name}プレビュー", key=f"preview_{section_type}"):
                                st.session_state[f"preview_{section_type}"] = True
                    else:
                        st.info(f"💡 {section_name}のテンプレートはまだありません")
    
    with col2:
        st.markdown("### Step 3: LP統合プレビュー")
        
        # 個別セクションプレビュー
        for section_type in SECTION_LABELS.keys():
            if st.session_state.get(f"preview_{section_type}", False):
                if section_type in sections:
                    st.markdown(f"#### {SECTION_LABELS[section_type]}プレビュー")
                    html_preview = generate_section_preview(sections[section_type], brand_color)
                    st.components.v1.html(html_preview, height=400, scrolling=True)
                    
                    if st.button(f"❌ {SECTION_LABELS[section_type]}プレビューを閉じる", key=f"close_{section_type}"):
                        st.session_state[f"preview_{section_type}"] = False
                        st.rerun()
                    st.markdown("---")
        
        if sections:
            if st.button("🚀 BtoB SaaS LP全体プレビュー生成", type="primary", use_container_width=True):
                st.markdown("#### 📋 LP構成")
                
                # LP構成の表示
                lp_structure = ""
                section_order = ["hero", "features", "testimonials", "how_it_works", "social_proof", "pricing", "faq", "cta"]
                
                used_sections = []
                for section_type in section_order:
                    if section_type in sections:
                        used_sections.append(section_type)
                        template = sections[section_type]
                        lp_structure += f"**{len(used_sections)}. {SECTION_LABELS[section_type]}**\n"
                        lp_structure += f"- {template['display_name']}\n"
                        content = template.get('content', {})
                        if content.get('title'):
                            lp_structure += f"- メイン: {content['title'][:50]}...\n"
                        lp_structure += "\n"
                
                st.text_area("LP構成", lp_structure, height=200)
                
                st.markdown("---")
                st.markdown("#### 🎯 BtoB SaaS LP統合プレビュー")
                
                # 統合HTMLプレビュー
                full_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
                    <style>
                        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
                        .section-separator { height: 1px; background: #E5E7EB; margin: 0; }
                    </style>
                </head>
                <body>
                """
                
                for section_type in section_order:
                    if section_type in sections:
                        section_html = generate_section_preview(sections[section_type], brand_color)
                        # body部分のみ抽出
                        if '<body>' in section_html and '</body>' in section_html:
                            section_content = section_html.split('<body>')[1].split('</body>')[0]
                            full_html += section_content
                            full_html += '<div class="section-separator"></div>'
                
                full_html += """
                </body>
                </html>
                """
                
                st.components.v1.html(full_html, height=2000, scrolling=True)
                
                st.markdown("---")
                st.markdown("#### 💾 完成LP出力")
                
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    st.download_button(
                        label="💾 完成LP HTMLをダウンロード",
                        data=full_html,
                        file_name="btob_saas_lp_complete.html",
                        mime="text/html",
                        use_container_width=True
                    )
                
                with col_dl2:
                    # JSON構成もダウンロード可能に
                    lp_config = {
                        "page_type": page_type,
                        "target": target,
                        "tone": tone,
                        "brand_color": brand_color,
                        "sections": {k: v["template_id"] for k, v in sections.items()},
                        "created_at": datetime.now().isoformat()
                    }
                    
                    st.download_button(
                        label="📋 LP構成JSONをダウンロード",
                        data=json.dumps(lp_config, ensure_ascii=False, indent=2),
                        file_name="lp_config.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.info("⬅️ 左側でセクションを選択してください")

def show_template_list():
    """テンプレート一覧画面（BtoB SaaS特化）"""
    st.markdown("## 📚 テンプレート一覧 - BtoB SaaS特化")
    
    templates = get_templates()
    
    if not templates:
        st.info("まだテンプレートがありません。「テンプレート登録」から作成してください。")
        return
    
    # フィルター（カテゴリ別）
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("ステータス", ["all", "draft", "approved", "need_fix"])
    with col2:
        # カテゴリ別フィルター
        category_options = ["all"] + list(SECTION_CATEGORIES.keys())
        category_filter = st.selectbox("カテゴリ", category_options)
    with col3:
        # セクション別フィルター  
        if category_filter != "all" and category_filter in SECTION_CATEGORIES:
            section_options = ["all"] + list(SECTION_CATEGORIES[category_filter].keys())
            section_filter = st.selectbox("セクション", section_options)
        else:
            section_filter = st.selectbox("セクション", ["all"] + list(SECTION_LABELS.keys()))
    
    # フィルタリング
    filtered = templates
    if status_filter != "all":
        filtered = [t for t in filtered if t["status"] == status_filter]
    
    if category_filter != "all":
        # カテゴリに含まれるセクション
        category_sections = SECTION_CATEGORIES.get(category_filter, {}).keys()
        filtered = [t for t in filtered if t["section_type"] in category_sections]
    
    if section_filter != "all":
        filtered = [t for t in filtered if t["section_type"] == section_filter]
    
    st.markdown(f"### 📊 {len(filtered)}件のテンプレート")
    
    # カテゴリ別に整理して表示
    if category_filter == "all":
        # 全カテゴリ表示
        for category, section_dict in SECTION_CATEGORIES.items():
            category_templates = [t for t in filtered if t["section_type"] in section_dict.keys()]
            
            if category_templates:
                with st.expander(f"{category} ({len(category_templates)}件)", expanded=True):
                    display_template_cards(category_templates)
    else:
        # 選択カテゴリのみ表示
        display_template_cards(filtered)
    
    # テンプレート詳細モーダル
    if st.session_state.editing_template_id:
        show_saas_template_detail_modal()

def display_template_cards(templates):
    """テンプレートカードの表示"""
    for template in templates:
        status_colors = {
            "draft": ("bg-yellow-100", "text-yellow-800"),
            "approved": ("bg-green-100", "text-green-800"), 
            "need_fix": ("bg-red-100", "text-red-800")
        }
        bg_class, text_class = status_colors.get(template["status"], ("bg-gray-100", "text-gray-800"))
        
        # セクション種別のカテゴリ特定
        section_type = template["section_type"]
        category_name = "その他"
        for cat, sections in SECTION_CATEGORIES.items():
            if section_type in sections:
                category_name = cat
                break
        
        with st.container():
            st.markdown(f"""
            <div class="bg-white rounded-lg shadow-md p-6 mb-4 border border-gray-200">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">{template['display_name']}</h3>
                        <p class="text-gray-600 mt-2">{template.get('metadata', {}).get('description', '')}</p>
                    </div>
                    <div class="flex gap-2 flex-col">
                        <span class="px-3 py-1 {bg_class} {text_class} rounded-full text-sm font-semibold">
                            {template['status']}
                        </span>
                    </div>
                </div>
                <div class="flex gap-2 mb-3">
                    <span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">{SECTION_LABELS.get(section_type, section_type)}</span>
                    <span class="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs">{category_name}</span>
                    {''.join([f'<span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{tag}</span>' for tag in template.get('metadata', {}).get('tags', [])])}
                </div>
                <div class="text-sm text-gray-500">
                    作成日: {template.get('metadata', {}).get('created_at', '')} | ID: {template['template_id'][:8]}...
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

def show_saas_template_detail_modal():
    """BtoB SaaS特化テンプレート詳細モーダル"""
    template_id = st.session_state.editing_template_id
    template = get_template_by_id(template_id)
    
    if not template:
        st.error("テンプレートが見つかりません")
        st.session_state.editing_template_id = None
        return
    
    section_type = template.get("section_type", "")
    section_name = SECTION_LABELS.get(section_type, section_type)
    
    # モーダル風表示
    st.markdown("---")
    st.markdown(f"## 📝 テンプレート詳細: {template['display_name']} ({section_name})")
    
    col_close, _ = st.columns([1, 5])
    with col_close:
        if st.button("❌ 閉じる"):
            st.session_state.editing_template_id = None
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["👁️ プレビュー", "✏️ 基本編集", "🎯 セクション特化編集", "📋 JSON"])
    
    # プレビュータブ
    with tab1:
        st.markdown("### セクション特化プレビュー")
        html_preview = generate_section_preview(template)
        st.components.v1.html(html_preview, height=700, scrolling=True)
    
    # 基本編集タブ
    with tab2:
        st.markdown("### 基本コンテンツ編集")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_content = template.get('content', {})
            new_title = st.text_area("タイトル", value=current_content.get('title', ''), height=100, key="edit_title")
            new_subtitle = st.text_area("サブタイトル", value=current_content.get('subtitle', ''), height=100, key="edit_subtitle")
            new_cta = st.text_input("CTAラベル", value=current_content.get('cta_label', ''), key="edit_cta")
        
        with col2:
            current_layout = template.get('layout', {})
            new_alignment = st.selectbox("配置", ["left", "center", "right"], 
                                        index=["left", "center", "right"].index(current_layout.get('alignment', 'center')),
                                        key="edit_align")
            new_bg_color = st.color_picker("背景色", value=current_layout.get('background_color', '#FFFFFF'), key="edit_bg")
        
        if st.button("💾 基本更新を保存", type="primary"):
            updates = {
                "content": {
                    **current_content,
                    "title": new_title,
                    "subtitle": new_subtitle,
                    "cta_label": new_cta
                },
                "layout": {
                    **current_layout,
                    "alignment": new_alignment,
                    "background_color": new_bg_color
                }
            }
            update_template(template_id, updates)
            st.success("✅ 基本情報を更新しました！")
            st.rerun()
    
    # セクション特化編集タブ
    with tab3:
        st.markdown(f"### 🎯 {section_name}特化編集")
        
        # セクション別の特化編集UI
        if section_type == "features":
            show_features_editor(template)
        elif section_type == "testimonials":
            show_testimonials_editor(template)
        elif section_type == "how_it_works":
            show_how_it_works_editor(template)
        elif section_type == "social_proof":
            show_social_proof_editor(template)
        elif section_type == "faq":
            show_faq_editor(template)
        else:
            st.info(f"💡 {section_name}の特化編集機能は準備中です。「基本編集」タブをご利用ください。")
    
    # JSONタブ
    with tab4:
        st.markdown("### JSON表示")
        st.json(template)
        
        st.download_button(
            label="💾 JSONをダウンロード",
            data=json.dumps(template, ensure_ascii=False, indent=2),
            file_name=f"template_{section_type}_{template['template_id']}.json",
            mime="application/json"
        )

def show_features_editor(template):
    """機能紹介セクション特化編集"""
    content = template.get('content', {})
    features = content.get('features', [])
    
    st.markdown("#### 機能一覧編集")
    
    # 既存機能の編集
    for i, feature in enumerate(features):
        st.markdown(f"**機能 {i+1}**")
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            if isinstance(feature, dict):
                icon = st.text_input("アイコン", value=feature.get('icon', '🔧'), key=f"feature_icon_{i}")
        with col2:
            if isinstance(feature, dict):
                title = st.text_input("機能名", value=feature.get('title', ''), key=f"feature_title_{i}")
        with col3:
            if isinstance(feature, dict):
                desc = st.text_input("説明", value=feature.get('description', ''), key=f"feature_desc_{i}")
    
    # 新機能追加
    st.markdown("---")
    st.markdown("#### 新機能追加")
    col1, col2, col3 = st.columns([1, 2, 3])
    
    with col1:
        new_icon = st.text_input("アイコン", value="📊", key="new_feature_icon")
    with col2:
        new_title = st.text_input("機能名", key="new_feature_title")
    with col3:
        new_desc = st.text_input("説明", key="new_feature_desc")
    
    if st.button("➕ 機能を追加"):
        if new_title and new_desc:
            new_feature = {
                "icon": new_icon,
                "title": new_title,
                "description": new_desc
            }
            features.append(new_feature)
            
            updates = {
                "content": {
                    **content,
                    "features": features
                }
            }
            update_template(template["template_id"], updates)
            st.success("機能を追加しました！")
            st.rerun()

def show_testimonials_editor(template):
    """お客様の声セクション特化編集"""
    content = template.get('content', {})
    testimonials = content.get('testimonials', [])
    
    st.markdown("#### お客様の声一覧")
    
    for i, testimonial in enumerate(testimonials):
        if isinstance(testimonial, dict):
            st.markdown(f"**お客様 {i+1}**")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("お名前", value=testimonial.get('name', ''), key=f"test_name_{i}")
                company = st.text_input("会社・役職", value=testimonial.get('company', ''), key=f"test_company_{i}")
            with col2:
                avatar = st.text_input("アバター", value=testimonial.get('avatar', '👤'), key=f"test_avatar_{i}")
                rating = st.selectbox("評価", [1,2,3,4,5], index=testimonial.get('rating', 5)-1, key=f"test_rating_{i}")
            
            comment = st.text_area("コメント", value=testimonial.get('comment', ''), key=f"test_comment_{i}")

def show_how_it_works_editor(template):
    """利用の流れセクション特化編集"""
    st.info("利用の流れの詳細編集機能は準備中です。")

def show_social_proof_editor(template):
    """導入企業セクション特化編集"""
    st.info("導入企業の詳細編集機能は準備中です。")

def show_faq_editor(template):
    """FAQ セクション特化編集"""
    st.info("FAQ の詳細編集機能は準備中です。")

def show_data_management():
    """データ管理画面"""
    st.markdown("## 💾 データ管理")
    st.markdown("BtoB SaaS特化テンプレートデータの管理ができます。")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 エクスポート")
        st.info("現在のBtoB SaaS特化テンプレートデータをJSON形式でダウンロードできます。")
        
        json_data = export_templates_json()
        
        st.download_button(
            label="💾 BtoB SaaS テンプレートJSONをダウンロード",
            data=json_data,
            file_name=f"btob_saas_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # セクション別統計
        templates = get_templates()
        section_stats = {}
        for template in templates:
            section = template.get("section_type", "unknown")
            section_stats[section] = section_stats.get(section, 0) + 1
        
        st.markdown("#### セクション別統計")
        for section, count in section_stats.items():
            section_label = SECTION_LABELS.get(section, section)
            st.write(f"- {section_label}: {count}件")
        
        with st.expander("📋 JSONプレビュー"):
            st.code(json_data, language="json")
    
    with col2:
        st.markdown("### 📥 インポート")
        st.info("以前エクスポートしたBtoB SaaS特化JSONファイルを読み込めます。")
        
        uploaded_file = st.file_uploader("JSONファイルを選択", type=["json"])
        
        if uploaded_file is not None:
            try:
                imported_data = json.load(uploaded_file)
                
                if "templates" in imported_data:
                    # セクション別集計
                    import_section_stats = {}
                    for template in imported_data["templates"]:
                        section = template.get("section_type", "unknown")
                        import_section_stats[section] = import_section_stats.get(section, 0) + 1
                    
                    st.success(f"✅ {len(imported_data['templates'])}件のテンプレートを読み込みました")
                    
                    st.markdown("**インポート予定のセクション別件数:**")
                    for section, count in import_section_stats.items():
                        section_label = SECTION_LABELS.get(section, section)
                        st.write(f"- {section_label}: {count}件")
                    
                    if st.button("📥 BtoB SaaS テンプレートをインポート実行", type="primary", use_container_width=True):
                        st.session_state.templates = imported_data["templates"]
                        st.success("BtoB SaaS特化テンプレートのインポートが完了しました！")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("⚠️ 正しいJSON形式ではありません")
            except Exception as e:
                st.error(f"⚠️ エラー: {str(e)}")

# ===== エントリーポイント =====

if __name__ == "__main__":
    main()