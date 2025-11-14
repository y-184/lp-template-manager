import streamlit as st
import json
import re
import html
from pathlib import Path
from datetime import datetime
import uuid

# ページ設定
st.set_page_config(
    page_title="LP Template Manager - Jobs Quality Standard",
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== セキュリティ強化関数（Jobs基準） =====

def sanitize_html(content):
    """
    HTML/JavaScriptの危険なタグを無害化
    XSS攻撃を防御し、安全な表示用HTMLを生成
    """
    if not isinstance(content, str):
        return str(content)
    
    # 危険なタグとスクリプトを除去
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>', 
        r'javascript:',
        r'on\w+\s*=',
        r'<embed[^>]*>',
        r'<object[^>]*>.*?</object>'
    ]
    
    cleaned = content
    for pattern in dangerous_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
    # HTMLエスケープ
    cleaned = html.escape(cleaned)
    
    # 基本的なフォーマットタグのみ許可
    safe_tags = {
        '&lt;b&gt;': '<b>', '&lt;/b&gt;': '</b>',
        '&lt;strong&gt;': '<strong>', '&lt;/strong&gt;': '</strong>', 
        '&lt;i&gt;': '<i>', '&lt;/i&gt;': '</i>',
        '&lt;em&gt;': '<em>', '&lt;/em&gt;': '</em>',
        '&lt;br&gt;': '<br>', '&lt;br/&gt;': '<br/>',
        '&lt;p&gt;': '<p>', '&lt;/p&gt;': '</p>',
        '&lt;div&gt;': '<div>', '&lt;/div&gt;': '</div>',
        '&lt;span&gt;': '<span>', '&lt;/span&gt;': '</span>'
    }
    
    for escaped, safe in safe_tags.items():
        cleaned = cleaned.replace(escaped, safe)
    
    return cleaned

def validate_json_structure(data, section_type):
    """
    JSONデータ構造の妥当性を検証
    必須フィールドの存在と型をチェック
    """
    if not isinstance(data, dict):
        return False, "データが辞書形式ではありません"
    
    # セクション別必須フィールド定義
    required_fields = {
        'hero': ['title', 'subtitle'],
        'features': ['title', 'features_list'],
        'testimonials': ['title', 'testimonials'],
        'social_proof': ['title', 'companies'],
        'faq': ['title', 'questions']
    }
    
    if section_type not in required_fields:
        return True, "検証対象外のセクション"
    
    missing_fields = []
    for field in required_fields[section_type]:
        if not safe_get_nested(data, field):
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"必須フィールドが不足: {', '.join(missing_fields)}"
    
    return True, "検証OK"

def safe_html_generation(template_data):
    """
    安全なHTML生成（XSS防御統合）
    すべてのユーザー入力をサニタイズしてHTML出力
    """
    try:
        if not isinstance(template_data, dict):
            return "<p>テンプレートデータが無効です</p>"
        
        # データをサニタイズ
        safe_data = {}
        for key, value in template_data.items():
            if isinstance(value, str):
                safe_data[key] = sanitize_html(value)
            elif isinstance(value, list):
                safe_data[key] = [sanitize_html(str(item)) for item in value]
            elif isinstance(value, dict):
                safe_data[key] = {k: sanitize_html(str(v)) for k, v in value.items()}
            else:
                safe_data[key] = sanitize_html(str(value))
        
        return generate_section_html(safe_data)
    
    except Exception as e:
        return f"<p>HTML生成エラー: {html.escape(str(e))}</p>"

def handle_error_gracefully(func, fallback_message="処理中にエラーが発生しました"):
    """
    エラーハンドリング装飾子
    例外をキャッチしてユーザーフレンドリーなメッセージを表示
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"{fallback_message}: {str(e)}")
            return None
    return wrapper

# Tailwind CSS読み込み（セキュア版）
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

# ===== 強化されたJSON抽出関数 =====

def safe_get_nested(data, path, default=None):
    """
    ネストされたJSONから値を安全に取得（エラーハンドリング強化）
    """
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

@handle_error_gracefully
def extract_hero_data(template):
    """
    ヒーローセクション用データ抽出（エラーハンドリング強化）
    """
    # タイトル取得（複数パターン対応）
    title = (
        safe_get_nested(template, 'content.title') or
        safe_get_nested(template, 'title') or
        safe_get_nested(template, 'content.main_headline') or
        safe_get_nested(template, 'main_headline') or
        '【メインタイトル】'
    )
    
    # サブタイトル取得
    subtitle = (
        safe_get_nested(template, 'content.subtitle') or
        safe_get_nested(template, 'subtitle') or
        safe_get_nested(template, 'content.sub_headline') or
        safe_get_nested(template, 'sub_headline') or
        '【サブタイトル】'
    )
    
    # 説明文取得
    description = (
        safe_get_nested(template, 'content.description') or
        safe_get_nested(template, 'description') or
        safe_get_nested(template, 'content.message') or
        '【説明文】'
    )
    
    # CTA要素取得（新旧両対応）
    cta_primary = (
        safe_get_nested(template, 'cta.primary') or
        safe_get_nested(template, 'content.cta_primary') or
        safe_get_nested(template, 'cta_primary') or
        '無料で始める'
    )
    
    cta_secondary = (
        safe_get_nested(template, 'cta.secondary') or
        safe_get_nested(template, 'content.cta_secondary') or
        safe_get_nested(template, 'cta_secondary') or
        '資料をダウンロード'
    )
    
    # 信頼要素取得（新旧両対応）
    trust_elements = []
    
    # 新形式: social_proof_badges
    badges = safe_get_nested(template, 'social_proof_badges', [])
    if badges and isinstance(badges, list):
        trust_elements.extend(badges)
    
    # 従来形式: content.trust_badges
    old_badges = safe_get_nested(template, 'content.trust_badges', [])
    if old_badges and isinstance(old_badges, list):
        trust_elements.extend(old_badges)
    
    # 信頼要素がない場合のデフォルト
    if not trust_elements:
        trust_elements = ['導入企業1,000社突破', '満足度98%']
    
    return {
        'title': title,
        'subtitle': subtitle, 
        'description': description,
        'cta_primary': cta_primary,
        'cta_secondary': cta_secondary,
        'trust_elements': trust_elements,
        'image_description': safe_get_nested(template, 'hero_image_description', 'プロダクト画面'),
        'layout_type': safe_get_nested(template, 'layout_type', 'center')
    }

@handle_error_gracefully
def extract_features_data(template):
    """
    機能紹介セクション用データ抽出（エラーハンドリング強化）
    """
    section_title = (
        safe_get_nested(template, 'content.section_title') or
        safe_get_nested(template, 'section_title') or
        '主要機能'
    )
    
    intro = (
        safe_get_nested(template, 'content.introduction') or
        safe_get_nested(template, 'introduction') or
        ''
    )
    
    # 機能リスト取得（新旧両対応）
    features = []
    
    # 新形式: features配列
    feature_list = safe_get_nested(template, 'features', [])
    if feature_list and isinstance(feature_list, list):
        for feature in feature_list:
            if isinstance(feature, dict):
                features.append({
                    'title': safe_get_nested(feature, 'title', '機能名'),
                    'description': safe_get_nested(feature, 'description', '機能説明'),
                    'icon': safe_get_nested(feature, 'icon', '⚡')
                })
    
    # 従来形式: content.features
    old_features = safe_get_nested(template, 'content.features', [])
    if old_features and isinstance(old_features, list) and not features:
        for feature in old_features:
            if isinstance(feature, dict):
                features.append({
                    'title': safe_get_nested(feature, 'title', '機能名'),
                    'description': safe_get_nested(feature, 'description', '機能説明'),
                    'icon': safe_get_nested(feature, 'icon', '⚡')
                })
    
    # デフォルト機能
    if not features:
        features = [
            {'title': '高速処理', 'description': '従来比10倍の処理速度', 'icon': '⚡'},
            {'title': '簡単操作', 'description': 'ドラッグ&ドロップで直感的', 'icon': '🎯'},
            {'title': '安全性', 'description': 'エンタープライズ級セキュリティ', 'icon': '🛡️'}
        ]
    
    return {
        'section_title': section_title,
        'introduction': intro,
        'features': features
    }

@handle_error_gracefully  
def extract_testimonials_data(template):
    """
    お客様の声セクション用データ抽出（エラーハンドリング強化）
    """
    section_title = (
        safe_get_nested(template, 'content.section_title') or
        safe_get_nested(template, 'section_title') or
        'お客様の声'
    )
    
    testimonials = []
    
    # テスティモニアルリスト取得
    testimonial_list = (
        safe_get_nested(template, 'testimonials') or
        safe_get_nested(template, 'content.testimonials') or
        []
    )
    
    if testimonial_list and isinstance(testimonial_list, list):
        for testimonial in testimonial_list:
            if isinstance(testimonial, dict):
                testimonials.append({
                    'quote': safe_get_nested(testimonial, 'quote', 'お客様コメント'),
                    'author': safe_get_nested(testimonial, 'author', '匿名'),
                    'company': safe_get_nested(testimonial, 'company', '企業名'),
                    'position': safe_get_nested(testimonial, 'position', '役職')
                })
    
    # デフォルトテスティモニアル
    if not testimonials:
        testimonials = [
            {
                'quote': '導入後、業務効率が劇的に向上しました',
                'author': '田中様',
                'company': 'A株式会社', 
                'position': '部長'
            }
        ]
    
    return {
        'section_title': section_title,
        'testimonials': testimonials
    }

@handle_error_gracefully
def extract_social_proof_data(template):
    """
    導入企業セクション用データ抽出（エラーハンドリング強化）
    """
    section_title = (
        safe_get_nested(template, 'content.section_title') or
        safe_get_nested(template, 'section_title') or
        '導入企業'
    )
    
    companies = []
    
    # 企業リスト取得
    company_list = (
        safe_get_nested(template, 'companies') or
        safe_get_nested(template, 'content.companies') or
        []
    )
    
    if company_list and isinstance(company_list, list):
        companies = [str(company) for company in company_list]
    
    # デフォルト企業
    if not companies:
        companies = ['大手IT企業A社', '製造業B社', 'サービス業C社']
    
    # 統計情報
    stats = safe_get_nested(template, 'stats', {})
    if not stats:
        stats = {
            'total_companies': '1,000',
            'satisfaction_rate': '98',
            'active_users': '50,000'
        }
    
    return {
        'section_title': section_title,
        'companies': companies,
        'stats': stats
    }

@handle_error_gracefully
def extract_faq_data(template):
    """
    FAQ セクション用データ抽出（エラーハンドリング強化）
    """
    section_title = (
        safe_get_nested(template, 'content.section_title') or
        safe_get_nested(template, 'section_title') or
        'よくある質問'
    )
    
    questions = []
    
    # FAQ リスト取得
    faq_list = (
        safe_get_nested(template, 'questions') or
        safe_get_nested(template, 'content.questions') or
        safe_get_nested(template, 'faqs') or
        []
    )
    
    if faq_list and isinstance(faq_list, list):
        for faq in faq_list:
            if isinstance(faq, dict):
                questions.append({
                    'question': safe_get_nested(faq, 'question', '質問'),
                    'answer': safe_get_nested(faq, 'answer', '回答')
                })
    
    # デフォルト FAQ
    if not questions:
        questions = [
            {
                'question': '無料トライアルはありますか？',
                'answer': 'はい、14日間の無料トライアルをご利用いただけます。'
            },
            {
                'question': '導入にはどのくらいの期間が必要ですか？',
                'answer': '通常、1〜2週間で導入が完了します。'
            }
        ]
    
    return {
        'section_title': section_title,
        'questions': questions
    }

# ===== セキュアHTML生成関数 =====

def generate_section_html(template_data):
    """
    セクションHTMLを安全に生成（XSS対策済み）
    """
    try:
        section_type = template_data.get('section_type', 'hero')
        
        if section_type == 'hero':
            return generate_hero_html(extract_hero_data(template_data))
        elif section_type == 'features':
            return generate_features_html(extract_features_data(template_data))
        elif section_type == 'testimonials':
            return generate_testimonials_html(extract_testimonials_data(template_data))
        elif section_type == 'social_proof':
            return generate_social_proof_html(extract_social_proof_data(template_data))
        elif section_type == 'faq':
            return generate_faq_html(extract_faq_data(template_data))
        else:
            return f"<p>未対応のセクション: {html.escape(section_type)}</p>"
    
    except Exception as e:
        return f"<p>HTML生成エラー: {html.escape(str(e))}</p>"

def generate_hero_html(data):
    """
    ヒーローセクションHTML生成（セキュア版）
    """
    trust_badges = ""
    if data.get('trust_elements'):
        badges = [f"<span class='bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm'>{sanitize_html(str(badge))}</span>" 
                 for badge in data['trust_elements']]
        trust_badges = f"<div class='flex flex-wrap gap-2 justify-center mt-4'>{''.join(badges)}</div>"
    
    return f"""
    <div class='bg-gradient-to-br from-blue-50 to-indigo-100 py-16 px-6'>
        <div class='max-w-6xl mx-auto text-center'>
            <h1 class='text-5xl font-bold text-gray-900 mb-6 leading-tight'>
                {sanitize_html(data.get('title', 'タイトル'))}
            </h1>
            <p class='text-xl text-gray-600 mb-4 max-w-3xl mx-auto'>
                {sanitize_html(data.get('subtitle', 'サブタイトル'))}
            </p>
            <p class='text-gray-500 mb-8 max-w-2xl mx-auto'>
                {sanitize_html(data.get('description', '説明文'))}
            </p>
            
            <div class='flex flex-col sm:flex-row gap-4 justify-center mb-8'>
                <button class='bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors'>
                    {sanitize_html(data.get('cta_primary', '無料で始める'))}
                </button>
                <button class='border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg font-semibold hover:border-gray-400 transition-colors'>
                    {sanitize_html(data.get('cta_secondary', '資料請求'))}
                </button>
            </div>
            
            {trust_badges}
            
            <div class='mt-12 bg-white rounded-lg shadow-lg p-4 max-w-4xl mx-auto'>
                <div class='bg-gray-100 rounded-lg h-64 flex items-center justify-center'>
                    <p class='text-gray-500'>{sanitize_html(data.get('image_description', 'プロダクト画面'))}</p>
                </div>
            </div>
        </div>
    </div>
    """

def generate_features_html(data):
    """
    機能セクションHTML生成（セキュア版）
    """
    features_html = ""
    if data.get('features'):
        for feature in data['features']:
            features_html += f"""
            <div class='bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow'>
                <div class='text-3xl mb-4'>{sanitize_html(str(feature.get('icon', '⚡')))}</div>
                <h3 class='text-xl font-semibold text-gray-900 mb-2'>
                    {sanitize_html(feature.get('title', '機能名'))}
                </h3>
                <p class='text-gray-600'>{sanitize_html(feature.get('description', '機能説明'))}</p>
            </div>
            """
    
    return f"""
    <div class='bg-white py-16 px-6'>
        <div class='max-w-6xl mx-auto'>
            <div class='text-center mb-12'>
                <h2 class='text-4xl font-bold text-gray-900 mb-4'>
                    {sanitize_html(data.get('section_title', '主要機能'))}
                </h2>
                <p class='text-gray-600 max-w-2xl mx-auto'>
                    {sanitize_html(data.get('introduction', ''))}
                </p>
            </div>
            
            <div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'>
                {features_html}
            </div>
        </div>
    </div>
    """

def generate_testimonials_html(data):
    """
    テスティモニアルセクションHTML生成（セキュア版）
    """
    testimonials_html = ""
    if data.get('testimonials'):
        for testimonial in data['testimonials']:
            testimonials_html += f"""
            <div class='bg-white rounded-lg p-6 shadow-md'>
                <p class='text-gray-700 mb-4 italic'>
                    "{sanitize_html(testimonial.get('quote', 'コメント'))}"
                </p>
                <div class='border-t pt-4'>
                    <p class='font-semibold text-gray-900'>
                        {sanitize_html(testimonial.get('author', '匿名'))}
                    </p>
                    <p class='text-sm text-gray-600'>
                        {sanitize_html(testimonial.get('position', ''))} - {sanitize_html(testimonial.get('company', ''))}
                    </p>
                </div>
            </div>
            """
    
    return f"""
    <div class='bg-gray-50 py-16 px-6'>
        <div class='max-w-6xl mx-auto'>
            <h2 class='text-4xl font-bold text-center text-gray-900 mb-12'>
                {sanitize_html(data.get('section_title', 'お客様の声'))}
            </h2>
            
            <div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'>
                {testimonials_html}
            </div>
        </div>
    </div>
    """

def generate_social_proof_html(data):
    """
    導入企業セクションHTML生成（セキュア版）
    """
    companies_html = ""
    if data.get('companies'):
        for company in data['companies']:
            companies_html += f"""
            <div class='bg-white rounded-lg p-4 shadow-sm flex items-center justify-center'>
                <span class='text-gray-700 font-medium'>{sanitize_html(str(company))}</span>
            </div>
            """
    
    stats = data.get('stats', {})
    stats_html = f"""
    <div class='grid grid-cols-1 md:grid-cols-3 gap-8 mb-12'>
        <div class='text-center'>
            <div class='text-4xl font-bold text-blue-600'>{sanitize_html(str(stats.get('total_companies', '1,000')))}</div>
            <div class='text-gray-600 mt-2'>導入企業数</div>
        </div>
        <div class='text-center'>
            <div class='text-4xl font-bold text-blue-600'>{sanitize_html(str(stats.get('satisfaction_rate', '98')))}%</div>
            <div class='text-gray-600 mt-2'>顧客満足度</div>
        </div>
        <div class='text-center'>
            <div class='text-4xl font-bold text-blue-600'>{sanitize_html(str(stats.get('active_users', '50,000')))}</div>
            <div class='text-gray-600 mt-2'>アクティブユーザー</div>
        </div>
    </div>
    """
    
    return f"""
    <div class='bg-white py-16 px-6'>
        <div class='max-w-6xl mx-auto'>
            <h2 class='text-4xl font-bold text-center text-gray-900 mb-12'>
                {sanitize_html(data.get('section_title', '導入企業'))}
            </h2>
            
            {stats_html}
            
            <div class='grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4'>
                {companies_html}
            </div>
        </div>
    </div>
    """

def generate_faq_html(data):
    """
    FAQセクションHTML生成（セキュア版）
    """
    questions_html = ""
    if data.get('questions'):
        for i, faq in enumerate(data['questions']):
            questions_html += f"""
            <div class='border-b border-gray-200 py-4'>
                <button class='flex justify-between items-center w-full text-left' onclick='toggleFaq({i})'>
                    <h3 class='font-semibold text-gray-900'>
                        {sanitize_html(faq.get('question', '質問'))}
                    </h3>
                    <svg class='w-5 h-5 text-gray-500' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                        <path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'></path>
                    </svg>
                </button>
                <div id='faq-{i}' class='hidden mt-3'>
                    <p class='text-gray-600'>{sanitize_html(faq.get('answer', '回答'))}</p>
                </div>
            </div>
            """
    
    return f"""
    <div class='bg-gray-50 py-16 px-6'>
        <div class='max-w-4xl mx-auto'>
            <h2 class='text-4xl font-bold text-center text-gray-900 mb-12'>
                {sanitize_html(data.get('section_title', 'よくある質問'))}
            </h2>
            
            <div class='bg-white rounded-lg shadow-md p-6'>
                {questions_html}
            </div>
        </div>
    </div>
    
    <script>
    function toggleFaq(index) {{
        const element = document.getElementById('faq-' + index);
        if (element.classList.contains('hidden')) {{
            element.classList.remove('hidden');
        }} else {{
            element.classList.add('hidden');
        }}
    }}
    </script>
    """

# ===== セッションステート管理（エラー対応強化） =====

def init_session_state():
    """
    セッションステート初期化（エラーハンドリング強化）
    """
    try:
        if 'templates' not in st.session_state:
            st.session_state.templates = {}
        if 'selected_template' not in st.session_state:
            st.session_state.selected_template = None
        if 'current_mode' not in st.session_state:
            st.session_state.current_mode = "template_registration"
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
    except Exception as e:
        st.error(f"セッション初期化エラー: {str(e)}")

@handle_error_gracefully
def save_template(template_data):
    """
    テンプレートを安全に保存（JSON検証付き）
    """
    if not isinstance(template_data, dict):
        st.error("無効なテンプレートデータです")
        return False
    
    # 必須フィールドチェック
    if not template_data.get('name'):
        st.error("テンプレート名が必要です")
        return False
    
    # JSON構造検証
    section_type = template_data.get('section_type', 'hero')
    is_valid, message = validate_json_structure(template_data, section_type)
    
    if not is_valid:
        st.error(f"データ検証エラー: {message}")
        return False
    
    # セッションステートに安全に保存
    template_id = str(uuid.uuid4())
    template_data['id'] = template_id
    template_data['created_at'] = datetime.now().isoformat()
    
    st.session_state.templates[template_id] = template_data
    st.success("テンプレートが保存されました")
    return True

# ===== 完全実装エディター関数 =====

def show_social_proof_editor(template):
    """
    導入企業エディター（完全実装版）
    """
    st.subheader("📊 導入企業セクション編集")
    
    # データ抽出
    data = extract_social_proof_data(template)
    
    # セクションタイトル編集
    section_title = st.text_input(
        "セクションタイトル",
        value=data.get('section_title', '導入企業'),
        key="social_proof_title"
    )
    
    # 統計情報編集
    st.write("### 統計情報")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_companies = st.text_input(
            "導入企業数",
            value=data.get('stats', {}).get('total_companies', '1,000'),
            key="social_proof_companies"
        )
    
    with col2:
        satisfaction_rate = st.text_input(
            "満足度（%）",
            value=data.get('stats', {}).get('satisfaction_rate', '98'),
            key="social_proof_satisfaction"
        )
    
    with col3:
        active_users = st.text_input(
            "アクティブユーザー数", 
            value=data.get('stats', {}).get('active_users', '50,000'),
            key="social_proof_users"
        )
    
    # 企業リスト編集
    st.write("### 導入企業一覧")
    companies = data.get('companies', [])
    
    # 企業追加
    new_company = st.text_input("新しい企業名を追加", key="new_company_input")
    if st.button("企業を追加", key="add_company"):
        if new_company.strip():
            companies.append(new_company.strip())
            st.success(f"{new_company} を追加しました")
    
    # 既存企業の編集・削除
    for i, company in enumerate(companies):
        col1, col2 = st.columns([3, 1])
        with col1:
            companies[i] = st.text_input(f"企業 {i+1}", value=company, key=f"company_{i}")
        with col2:
            if st.button("削除", key=f"delete_company_{i}"):
                companies.pop(i)
                st.rerun()
    
    # プレビューボタン
    if st.button("プレビュー更新", key="social_proof_preview"):
        updated_data = {
            'section_type': 'social_proof',
            'section_title': section_title,
            'companies': companies,
            'stats': {
                'total_companies': total_companies,
                'satisfaction_rate': satisfaction_rate,
                'active_users': active_users
            }
        }
        
        # 安全なHTML生成
        preview_html = safe_html_generation(updated_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)

def show_faq_editor(template):
    """
    FAQエディター（完全実装版）
    """
    st.subheader("❓ FAQ セクション編集")
    
    # データ抽出
    data = extract_faq_data(template)
    
    # セクションタイトル編集
    section_title = st.text_input(
        "セクションタイトル",
        value=data.get('section_title', 'よくある質問'),
        key="faq_title"
    )
    
    # FAQ リスト編集
    st.write("### FAQ 一覧")
    questions = data.get('questions', [])
    
    # 新規FAQ追加
    st.write("#### 新しいFAQを追加")
    col1, col2 = st.columns(2)
    with col1:
        new_question = st.text_area("質問", key="new_faq_question")
    with col2:
        new_answer = st.text_area("回答", key="new_faq_answer")
    
    if st.button("FAQを追加", key="add_faq"):
        if new_question.strip() and new_answer.strip():
            questions.append({
                'question': new_question.strip(),
                'answer': new_answer.strip()
            })
            st.success("FAQを追加しました")
    
    # 既存FAQ編集
    st.write("#### 既存FAQ編集")
    for i, faq in enumerate(questions):
        with st.expander(f"FAQ {i+1}: {faq.get('question', '')[:50]}..."):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                questions[i]['question'] = st.text_area(
                    f"質問 {i+1}",
                    value=faq.get('question', ''),
                    key=f"faq_question_{i}"
                )
            
            with col2:
                questions[i]['answer'] = st.text_area(
                    f"回答 {i+1}",
                    value=faq.get('answer', ''),
                    key=f"faq_answer_{i}"
                )
            
            with col3:
                if st.button("削除", key=f"delete_faq_{i}"):
                    questions.pop(i)
                    st.rerun()
    
    # プレビューボタン
    if st.button("プレビュー更新", key="faq_preview"):
        updated_data = {
            'section_type': 'faq',
            'section_title': section_title,
            'questions': questions
        }
        
        # 安全なHTML生成
        preview_html = safe_html_generation(updated_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)

# ===== 他のエディター関数（既存）=====

def show_hero_editor(template):
    """
    ヒーローセクションエディター
    """
    st.subheader("🎯 ヒーローセクション編集")
    
    # データ抽出
    data = extract_hero_data(template)
    
    # タイトル編集
    title = st.text_input("メインタイトル", value=data.get('title', ''), key="hero_title")
    subtitle = st.text_input("サブタイトル", value=data.get('subtitle', ''), key="hero_subtitle")
    description = st.text_area("説明文", value=data.get('description', ''), key="hero_description")
    
    # CTA編集
    col1, col2 = st.columns(2)
    with col1:
        cta_primary = st.text_input("主要CTAボタン", value=data.get('cta_primary', ''), key="hero_cta_primary")
    with col2:
        cta_secondary = st.text_input("副次CTAボタン", value=data.get('cta_secondary', ''), key="hero_cta_secondary")
    
    # 信頼要素編集
    st.write("### 信頼要素")
    trust_elements = data.get('trust_elements', [])
    
    # 新しい信頼要素追加
    new_element = st.text_input("新しい信頼要素を追加", key="new_trust_element")
    if st.button("追加", key="add_trust_element"):
        if new_element.strip():
            trust_elements.append(new_element.strip())
    
    # 既存要素の編集
    for i, element in enumerate(trust_elements):
        col1, col2 = st.columns([3, 1])
        with col1:
            trust_elements[i] = st.text_input(f"信頼要素 {i+1}", value=element, key=f"trust_element_{i}")
        with col2:
            if st.button("削除", key=f"delete_trust_{i}"):
                trust_elements.pop(i)
                st.rerun()
    
    # プレビューボタン
    if st.button("プレビュー更新", key="hero_preview"):
        updated_data = {
            'section_type': 'hero',
            'title': title,
            'subtitle': subtitle,
            'description': description,
            'cta_primary': cta_primary,
            'cta_secondary': cta_secondary,
            'trust_elements': trust_elements,
            'image_description': data.get('image_description', 'プロダクト画面'),
            'layout_type': data.get('layout_type', 'center')
        }
        
        # 安全なHTML生成
        preview_html = safe_html_generation(updated_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)

def show_features_editor(template):
    """
    機能セクションエディター
    """
    st.subheader("⚡ 機能セクション編集")
    
    # データ抽出
    data = extract_features_data(template)
    
    # セクション情報
    section_title = st.text_input("セクションタイトル", value=data.get('section_title', ''), key="features_title")
    introduction = st.text_area("紹介文", value=data.get('introduction', ''), key="features_intro")
    
    # 機能リスト編集
    st.write("### 機能一覧")
    features = data.get('features', [])
    
    # 新機能追加
    st.write("#### 新しい機能を追加")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_title = st.text_input("機能名", key="new_feature_title")
    with col2:
        new_description = st.text_input("機能説明", key="new_feature_description")
    with col3:
        new_icon = st.text_input("アイコン", value="⚡", key="new_feature_icon")
    
    if st.button("機能を追加", key="add_feature"):
        if new_title.strip() and new_description.strip():
            features.append({
                'title': new_title.strip(),
                'description': new_description.strip(),
                'icon': new_icon.strip() or '⚡'
            })
            st.success("機能を追加しました")
    
    # 既存機能編集
    for i, feature in enumerate(features):
        with st.expander(f"機能 {i+1}: {feature.get('title', '')}"):
            col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
            
            with col1:
                features[i]['title'] = st.text_input(f"機能名 {i+1}", value=feature.get('title', ''), key=f"feature_title_{i}")
            
            with col2:
                features[i]['description'] = st.text_input(f"説明 {i+1}", value=feature.get('description', ''), key=f"feature_desc_{i}")
            
            with col3:
                features[i]['icon'] = st.text_input(f"アイコン {i+1}", value=feature.get('icon', '⚡'), key=f"feature_icon_{i}")
            
            with col4:
                if st.button("削除", key=f"delete_feature_{i}"):
                    features.pop(i)
                    st.rerun()
    
    # プレビューボタン
    if st.button("プレビュー更新", key="features_preview"):
        updated_data = {
            'section_type': 'features',
            'section_title': section_title,
            'introduction': introduction,
            'features': features
        }
        
        # 安全なHTML生成
        preview_html = safe_html_generation(updated_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)

def show_testimonials_editor(template):
    """
    テスティモニアルエディター
    """
    st.subheader("💬 お客様の声編集")
    
    # データ抽出
    data = extract_testimonials_data(template)
    
    # セクションタイトル
    section_title = st.text_input("セクションタイトル", value=data.get('section_title', ''), key="testimonials_title")
    
    # テスティモニアル編集
    st.write("### お客様の声一覧")
    testimonials = data.get('testimonials', [])
    
    # 新しいテスティモニアル追加
    st.write("#### 新しいお客様の声を追加")
    col1, col2 = st.columns(2)
    with col1:
        new_quote = st.text_area("コメント", key="new_testimonial_quote")
        new_author = st.text_input("お名前", key="new_testimonial_author")
    with col2:
        new_company = st.text_input("会社名", key="new_testimonial_company")
        new_position = st.text_input("役職", key="new_testimonial_position")
    
    if st.button("お客様の声を追加", key="add_testimonial"):
        if new_quote.strip() and new_author.strip():
            testimonials.append({
                'quote': new_quote.strip(),
                'author': new_author.strip(),
                'company': new_company.strip(),
                'position': new_position.strip()
            })
            st.success("お客様の声を追加しました")
    
    # 既存テスティモニアル編集
    for i, testimonial in enumerate(testimonials):
        with st.expander(f"お客様の声 {i+1}: {testimonial.get('author', '')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                testimonials[i]['quote'] = st.text_area(
                    f"コメント {i+1}",
                    value=testimonial.get('quote', ''),
                    key=f"testimonial_quote_{i}"
                )
                testimonials[i]['author'] = st.text_input(
                    f"お名前 {i+1}",
                    value=testimonial.get('author', ''),
                    key=f"testimonial_author_{i}"
                )
            
            with col2:
                testimonials[i]['company'] = st.text_input(
                    f"会社名 {i+1}",
                    value=testimonial.get('company', ''),
                    key=f"testimonial_company_{i}"
                )
                testimonials[i]['position'] = st.text_input(
                    f"役職 {i+1}",
                    value=testimonial.get('position', ''),
                    key=f"testimonial_position_{i}"
                )
                
                if st.button("削除", key=f"delete_testimonial_{i}"):
                    testimonials.pop(i)
                    st.rerun()
    
    # プレビューボタン
    if st.button("プレビュー更新", key="testimonials_preview"):
        updated_data = {
            'section_type': 'testimonials',
            'section_title': section_title,
            'testimonials': testimonials
        }
        
        # 安全なHTML生成
        preview_html = safe_html_generation(updated_data)
        st.components.v1.html(preview_html, height=600, scrolling=True)

def show_how_it_works_editor(template):
    """
    利用の流れエディター（簡易実装）
    """
    st.subheader("🔄 利用の流れ編集")
    st.info("このセクションは現在開発中です。完全版では詳細な編集機能を提供予定です。")

# ===== メイン UI関数 =====

def main():
    """
    メインアプリケーション（セキュリティ強化版）
    """
    try:
        # セッション初期化
        init_session_state()
        
        # ヘッダー
        st.title("🚀 LP Template Manager - Jobs Quality Standard")
        st.markdown("**セキュリティ強化・エラーハンドリング完備版**")
        
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
        
        # モード別処理
        if st.session_state.current_mode == "template_registration":
            show_template_registration_mode()
        else:
            show_design_creation_mode()
            
        # エラーログ表示
        if st.session_state.get('error_log'):
            with st.sidebar:
                st.write("### ⚠️ エラーログ")
                for error in st.session_state.error_log[-5:]:  # 最新5件
                    st.error(error)
    
    except Exception as e:
        st.error(f"アプリケーションエラー: {str(e)}")
        if 'error_log' in st.session_state:
            st.session_state.error_log.append(f"メインエラー: {str(e)}")

@handle_error_gracefully
def show_template_registration_mode():
    """
    テンプレート登録モード
    """
    st.header("📝 テンプレート登録モード")
    
    # テンプレート基本情報
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
    
    # JSON入力エリア
    st.write("### 📄 JSONデータ入力")
    json_input = st.text_area(
        "ChatGPTから取得したJSONデータを貼り付けてください",
        height=200,
        key="json_input"
    )
    
    # JSONパース・プレビュー
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 JSONをパース", key="parse_json"):
            try:
                if json_input.strip():
                    # JSON解析
                    parsed_data = json.loads(json_input)
                    
                    # テンプレートデータ構築
                    template_data = {
                        'name': template_name or f"テンプレート_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'section_type': section_type,
                        'reference_url': reference_url,
                        'description': description,
                        'created_at': datetime.now().isoformat(),
                        **parsed_data  # JSONデータをマージ
                    }
                    
                    # セッションに一時保存
                    st.session_state.temp_template = template_data
                    st.success("JSONデータをパースしました！")
                else:
                    st.error("JSONデータを入力してください")
                    
            except json.JSONDecodeError as e:
                st.error(f"JSON解析エラー: {str(e)}")
            except Exception as e:
                st.error(f"パースエラー: {str(e)}")
    
    with col2:
        if st.button("💾 テンプレート保存", key="save_template"):
            if 'temp_template' in st.session_state:
                success = save_template(st.session_state.temp_template)
                if success:
                    del st.session_state.temp_template
            else:
                st.error("先にJSONをパースしてください")
    
    # プレビュー表示
    if 'temp_template' in st.session_state:
        st.write("### 👀 プレビュー")
        try:
            preview_html = safe_html_generation(st.session_state.temp_template)
            st.components.v1.html(preview_html, height=600, scrolling=True)
        except Exception as e:
            st.error(f"プレビュー生成エラー: {str(e)}")
    
    # 保存済みテンプレート一覧
    if st.session_state.templates:
        st.write("### 📚 保存済みテンプレート")
        for template_id, template in st.session_state.templates.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{template.get('name', '無名')}** ({SECTION_LABELS.get(template.get('section_type', 'unknown'), '不明')})")
            with col2:
                if st.button("プレビュー", key=f"preview_{template_id}"):
                    preview_html = safe_html_generation(template)
                    st.components.v1.html(preview_html, height=400, scrolling=True)
            with col3:
                if st.button("削除", key=f"delete_{template_id}"):
                    del st.session_state.templates[template_id]
                    st.rerun()

@handle_error_gracefully
def show_design_creation_mode():
    """
    デザイン作成モード
    """
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
        section_type = template.get('section_type', 'hero')
        
        # セクション別エディター表示
        if section_type == 'hero':
            show_hero_editor(template)
        elif section_type == 'features':
            show_features_editor(template)
        elif section_type == 'testimonials':
            show_testimonials_editor(template)
        elif section_type == 'social_proof':
            show_social_proof_editor(template)
        elif section_type == 'faq':
            show_faq_editor(template)
        elif section_type == 'how_it_works':
            show_how_it_works_editor(template)
        else:
            st.error(f"未対応のセクション: {section_type}")

# ===== アプリケーション実行 =====

if __name__ == "__main__":
    main()