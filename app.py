import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter
import numpy as np

# ページ設定
st.set_page_config(
    page_title="GEO分析ダッシュボード", 
    page_icon="🎯",
    layout="wide"
)

# メインタイトル
st.title("🎯 GEO分析ダッシュボード")
st.markdown("**Generative Engine Optimization (GEO) 分析ツール**")
st.markdown("---")

# サイドバー設定
st.sidebar.header("📊 分析設定")

# データアップロード
uploaded_file = st.sidebar.file_uploader(
    "CSVファイルをアップロード", 
    type=['csv'],
    help="プロンプト・回答データのCSVファイルをアップロードしてください"
)

# サンプルデータの読み込み（デモ用）
@st.cache_data
def load_sample_data():
    try:
        df = pd.read_csv('/home/user/LAVA_GEO_data.csv', header=None)
        # 列名を設定
        df.columns = ['ID', 'プロンプト', 'GPT回答', 'Gemini回答', 'Perplexity回答'] + [f'列{i}' for i in range(5, len(df.columns))]
        return df
    except:
        return None

# データの処理
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, header=None)
        # 列数に応じて列名を設定
        if len(df.columns) >= 5:
            df.columns = ['ID', 'プロンプト', 'GPT回答', 'Gemini回答', 'Perplexity回答'] + [f'列{i}' for i in range(5, len(df.columns))]
        else:
            df.columns = [f'列{i}' for i in range(len(df.columns))]
        
        st.sidebar.success(f"✅ ファイル読み込み完了: {len(df)}行")
        data_loaded = True
    except Exception as e:
        st.sidebar.error(f"❌ ファイル読み込みエラー: {e}")
        data_loaded = False
        df = None
else:
    # サンプルデータを使用
    df = load_sample_data()
    if df is not None:
        st.sidebar.info("📂 サンプルデータ（LAVA）を使用中")
        data_loaded = True
    else:
        st.sidebar.warning("⚠️ データファイルをアップロードしてください")
        data_loaded = False

if data_loaded and df is not None:
    
    # ブランド設定
    st.sidebar.subheader("🏢 ブランド設定")
    
    # メインブランド（分析対象）
    main_brand = st.sidebar.text_input(
        "メインブランド名", 
        value="LAVA",
        help="分析したいメインブランド名を入力"
    )
    
    # 競合ブランド
    competitors_input = st.sidebar.text_area(
        "競合ブランド（カンマ区切り）", 
        value="zen place, CALDO, loIve",
        help="競合ブランドをカンマ区切りで入力"
    )
    
    competitors = [brand.strip() for brand in competitors_input.split(',') if brand.strip()]
    
    # 分析関数
    def count_brand_mentions(text, brand_name):
        """テキスト内のブランド言及数をカウント"""
        if pd.isna(text) or text == '':
            return 0
        pattern = re.compile(re.escape(brand_name), re.IGNORECASE)
        return len(pattern.findall(str(text)))
    
    def extract_urls(text):
        """テキストからURLを抽出"""
        if pd.isna(text) or text == '':
            return []
        url_pattern = r'https?://[^\s\)\]\,]+'
        urls = re.findall(url_pattern, str(text))
        return urls
    
    # 分析実行
    if st.sidebar.button("🔍 分析実行", type="primary"):
        
        with st.spinner("分析中..."):
            
            # メイン分析結果を格納する辞書
            results = {}
            models = ['GPT', 'Gemini', 'Perplexity']
            model_columns = ['GPT回答', 'Gemini回答', 'Perplexity回答']
            
            # 各モデルでの分析
            for i, model in enumerate(models):
                if i + 2 < len(df.columns):  # 列が存在するかチェック
                    column = model_columns[i]
                    
                    # メインブランドの言及分析
                    main_mentions = df[column].apply(lambda x: count_brand_mentions(x, main_brand))
                    main_mention_rate = (main_mentions > 0).mean() * 100
                    
                    # 競合ブランドの言及分析
                    competitor_rates = {}
                    for competitor in competitors:
                        comp_mentions = df[column].apply(lambda x: count_brand_mentions(x, competitor))
                        competitor_rates[competitor] = (comp_mentions > 0).mean() * 100
                    
                    # URL分析
                    all_urls = []
                    for text in df[column].dropna():
                        urls = extract_urls(text)
                        all_urls.extend(urls)
                    
                    # ドメイン分析
                    domains = []
                    for url in all_urls:
                        try:
                            domain = re.findall(r'https?://([^/]+)', url)[0]
                            domains.append(domain)
                        except:
                            continue
                    
                    domain_counts = Counter(domains)
                    
                    results[model] = {
                        'main_brand_rate': main_mention_rate,
                        'competitor_rates': competitor_rates,
                        'total_urls': len(all_urls),
                        'unique_domains': len(domain_counts),
                        'top_domains': dict(domain_counts.most_common(10))
                    }
        
        # 結果表示
        st.header("📊 分析結果")
        
        # サマリーメトリクス
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_mention_rate = np.mean([results[model]['main_brand_rate'] for model in models if model in results])
            st.metric(
                f"{main_brand} 平均言及率",
                f"{avg_mention_rate:.1f}%",
                help="全AIモデルでの平均言及率"
            )
        
        with col2:
            best_model = max(results.keys(), key=lambda x: results[x]['main_brand_rate']) if results else "N/A"
            best_rate = results[best_model]['main_brand_rate'] if best_model != "N/A" else 0
            st.metric(
                "最高パフォーマンス",
                f"{best_model} ({best_rate:.1f}%)",
                help="最も言及率の高いAIモデル"
            )
        
        with col3:
            total_questions = len(df)
            st.metric(
                "総質問数",
                f"{total_questions}",
                help="分析対象の質問数"
            )
        
        with col4:
            total_urls = sum([results[model]['total_urls'] for model in results])
            st.metric(
                "総URL数",
                f"{total_urls}",
                help="全回答に含まれるURL総数"
            )
        
        # タブで詳細分析を分ける
        tab1, tab2, tab3, tab4 = st.tabs(["🏆 ブランド比較", "🤖 モデル別分析", "🔗 URL分析", "📝 詳細データ"])
        
        with tab1:
            st.subheader("ブランド言及率比較")
            
            # ブランド比較チャート作成
            brand_data = []
            
            for model in models:
                if model in results:
                    # メインブランド
                    brand_data.append({
                        'ブランド': main_brand,
                        'モデル': model,
                        '言及率': results[model]['main_brand_rate'],
                        'タイプ': 'メイン'
                    })
                    
                    # 競合ブランド
                    for competitor, rate in results[model]['competitor_rates'].items():
                        brand_data.append({
                            'ブランド': competitor,
                            'モデル': model,
                            '言及率': rate,
                            'タイプ': '競合'
                        })
            
            if brand_data:
                brand_df = pd.DataFrame(brand_data)
                
                # グループ化棒グラフ
                fig = px.bar(
                    brand_df, 
                    x='ブランド', 
                    y='言及率', 
                    color='モデル',
                    title=f"ブランド別・モデル別言及率比較",
                    labels={'言及率': '言及率 (%)', 'ブランド': 'ブランド名'},
                    height=400
                )
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # 平均言及率テーブル
                avg_rates = brand_df.groupby('ブランド')['言及率'].mean().sort_values(ascending=False)
                
                st.subheader("📈 ブランド別平均言及率ランキング")
                rank_df = pd.DataFrame({
                    'ランク': range(1, len(avg_rates) + 1),
                    'ブランド': avg_rates.index,
                    '平均言及率 (%)': avg_rates.values.round(1)
                })
                st.dataframe(rank_df, hide_index=True, use_container_width=True)
        
        with tab2:
            st.subheader("AIモデル別パフォーマンス")
            
            # モデル比較
            model_performance = []
            for model in models:
                if model in results:
                    model_performance.append({
                        'モデル': model,
                        f'{main_brand}言及率': results[model]['main_brand_rate'],
                        'URL引用数': results[model]['total_urls'],
                        'ユニークドメイン数': results[model]['unique_domains']
                    })
            
            if model_performance:
                perf_df = pd.DataFrame(model_performance)
                
                # レーダーチャート
                fig = go.Figure()
                
                angles = ['言及率', 'URL引用数', 'ユニークドメイン数']
                
                for _, row in perf_df.iterrows():
                    values = [
                        row[f'{main_brand}言及率'],
                        row['URL引用数'] / 10,  # スケール調整
                        row['ユニークドメイン数'] * 5  # スケール調整
                    ]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=angles,
                        fill='toself',
                        name=row['モデル']
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    title="モデル別パフォーマンス比較（正規化）",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 詳細テーブル
                st.dataframe(perf_df, hide_index=True, use_container_width=True)
        
        with tab3:
            st.subheader("URL・ドメイン分析")
            
            # 各モデルのトップドメイン
            col1, col2, col3 = st.columns(3)
            
            for i, (model, col) in enumerate(zip(models, [col1, col2, col3])):
                if model in results and results[model]['top_domains']:
                    with col:
                        st.markdown(f"**{model} トップドメイン**")
                        domains = list(results[model]['top_domains'].items())[:5]
                        
                        domain_df = pd.DataFrame(domains, columns=['ドメイン', '引用回数'])
                        
                        fig = px.bar(
                            domain_df,
                            x='引用回数',
                            y='ドメイン',
                            orientation='h',
                            title=f"{model} 引用ドメイン TOP5",
                            height=300
                        )
                        fig.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.subheader("詳細データ")
            
            # フィルター機能
            st.markdown("**データフィルター**")
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("プロンプト検索", placeholder="検索したいキーワードを入力")
            
            with col2:
                show_mentions_only = st.checkbox(f"{main_brand}が言及された行のみ表示")
            
            # データフィルタリング
            display_df = df.copy()
            
            if search_term:
                mask = display_df['プロンプト'].str.contains(search_term, case=False, na=False)
                display_df = display_df[mask]
            
            if show_mentions_only:
                # メインブランドが言及された行のみ
                mention_mask = False
                for col in ['GPT回答', 'Gemini回答', 'Perplexity回答']:
                    if col in display_df.columns:
                        col_mask = display_df[col].apply(lambda x: count_brand_mentions(x, main_brand) > 0)
                        mention_mask = mention_mask | col_mask
                
                if isinstance(mention_mask, pd.Series):
                    display_df = display_df[mention_mask]
            
            st.markdown(f"**表示件数: {len(display_df)} / {len(df)}**")
            
            # データ表示（最初の5列のみ）
            if len(display_df) > 0:
                display_columns = ['ID', 'プロンプト', 'GPT回答', 'Gemini回答', 'Perplexity回答']
                available_columns = [col for col in display_columns if col in display_df.columns]
                
                st.dataframe(
                    display_df[available_columns].head(50), 
                    height=400,
                    use_container_width=True
                )
                
                # CSVダウンロード
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 フィルター結果をCSVダウンロード",
                    data=csv,
                    file_name=f"geo_analysis_{main_brand}_filtered.csv",
                    mime="text/csv"
                )
            else:
                st.info("フィルター条件に該当するデータがありません。")

else:
    # データが読み込まれていない場合の案内
    st.info("📂 CSVファイルをアップロードするか、サンプルデータをお試しください。")
    
    st.markdown("""
    ### 📋 データ形式について
    
    **必要な列構成:**
    1. **ID** - 質問番号
    2. **プロンプト** - 質問内容
    3. **GPT回答** - ChatGPTの回答
    4. **Gemini回答** - Geminiの回答  
    5. **Perplexity回答** - Perplexityの回答
    
    **分析できる項目:**
    - ✅ ブランド言及率の比較
    - ✅ AIモデル別パフォーマンス
    - ✅ 競合他社との比較
    - ✅ URL引用分析
    - ✅ 詳細データの検索・フィルタリング
    """)

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🎯 GEO分析ダッシュボード | Powered by Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)
