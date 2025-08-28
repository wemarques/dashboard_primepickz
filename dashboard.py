import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Dashboard PrimePickz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_traffic_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    traffic_data = []
    base_visitors = 1200
    
    for date in dates:
        day_of_week = date.weekday()
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        growth_factor = 1 + (date - start_date).days * 0.002
        random_factor = np.random.normal(1, 0.15)
        
        visitors = int(base_visitors * weekend_factor * growth_factor * random_factor)
        pageviews = int(visitors * np.random.uniform(2.1, 3.8))
        bounce_rate = np.random.uniform(0.35, 0.65)
        avg_session_duration = np.random.uniform(120, 300)
        
        traffic_data.append({
            'date': date,
            'visitors': max(visitors, 100),
            'pageviews': max(pageviews, 200),
            'bounce_rate': bounce_rate,
            'avg_session_duration': avg_session_duration,
            'sessions': int(visitors * np.random.uniform(1.1, 1.4))
        })
    
    return pd.DataFrame(traffic_data)

@st.cache_data
def generate_affiliate_data():
    products = [
        {'name': 'iPhone 15 Pro', 'category': 'Eletronicos', 'commission_rate': 0.02},
        {'name': 'Creme Facial Neutrogena', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Kindle Paperwhite', 'category': 'Kindle', 'commission_rate': 0.04},
        {'name': 'Livro: Habitos Atomicos', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Whey Protein', 'category': 'Saude e Bem Estar', 'commission_rate': 0.05},
        {'name': 'MacBook Air M3', 'category': 'Eletronicos', 'commission_rate': 0.02},
        {'name': 'Serum Vitamina C', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Kindle Oasis', 'category': 'Kindle', 'commission_rate': 0.04},
        {'name': 'Livro: O Poder do Habito', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Omega 3', 'category': 'Saude e Bem Estar', 'commission_rate': 0.05},
        {'name': 'AirPods Pro', 'category': 'Eletronicos', 'commission_rate': 0.02},
        {'name': 'Base Liquida Maybelline', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Livro: Mindset', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Colageno Hidrolisado', 'category': 'Saude e Bem Estar', 'commission_rate': 0.05},
        {'name': 'iPad Air', 'category': 'Eletronicos', 'commission_rate': 0.02}
    ]
    
    affiliate_data = []
    
    for product in products:
        clicks = np.random.randint(50, 500)
        conversion_rate = np.random.uniform(0.02, 0.08)
        conversions = int(clicks * conversion_rate)
        avg_order_value = np.random.uniform(50, 800)
        commission_earned = conversions * avg_order_value * product['commission_rate']
        
        affiliate_data.append({
            'product_name': product['name'],
            'category': product['category'],
            'clicks': clicks,
            'conversions': conversions,
            'conversion_rate': conversion_rate,
            'commission_earned': commission_earned,
            'avg_order_value': avg_order_value
        })
    
    return pd.DataFrame(affiliate_data)

@st.cache_data
def generate_content_performance():
    posts = [
        {'title': '12 Livros que Mudam a Vida', 'category': 'Livros', 'publish_date': '2024-08-26'},
        {'title': 'Protecao Solar no Nordeste', 'category': 'Beleza', 'publish_date': '2024-08-26'},
        {'title': 'Kindle vs Paperwhite 2024', 'category': 'Kindle', 'publish_date': '2024-08-21'},
        {'title': 'Importancia da Leitura Infantil', 'category': 'Livros', 'publish_date': '2024-08-24'},
        {'title': 'Cuidados com Pele Seca', 'category': 'Beleza', 'publish_date': '2024-08-21'},
        {'title': 'Melhores Livros Infantis 2024', 'category': 'Livros', 'publish_date': '2024-08-19'},
        {'title': 'Rotina Skincare Perfeita', 'category': 'Beleza', 'publish_date': '2024-08-18'},
        {'title': 'Achados de Beleza', 'category': 'Beleza', 'publish_date': '2024-08-06'},
        {'title': 'Suplementos para Imunidade', 'category': 'Saude e Bem Estar', 'publish_date': '2024-08-15'},
        {'title': 'Kindle Unlimited Vale a Pena?', 'category': 'Kindle', 'publish_date': '2024-08-10'}
    ]
    
    content_data = []
    
    for post in posts:
        pageviews = np.random.randint(800, 5000)
        avg_time_on_page = np.random.uniform(180, 420)
        bounce_rate = np.random.uniform(0.25, 0.55)
        affiliate_clicks = np.random.randint(20, 200)
        social_shares = np.random.randint(5, 50)
        
        content_data.append({
            'title': post['title'],
            'category': post['category'],
            'publish_date': post['publish_date'],
            'pageviews': pageviews,
            'avg_time_on_page': avg_time_on_page,
            'bounce_rate': bounce_rate,
            'affiliate_clicks': affiliate_clicks,
            'social_shares': social_shares
        })
    
    return pd.DataFrame(content_data)

@st.cache_data
def generate_seo_data():
    keywords = [
        {'keyword': 'melhores livros 2024', 'position': 3, 'clicks': 1200, 'impressions': 15000},
        {'keyword': 'kindle paperwhite review', 'position': 5, 'clicks': 800, 'impressions': 12000},
        {'keyword': 'creme facial pele seca', 'position': 7, 'clicks': 600, 'impressions': 8500},
        {'keyword': 'livros desenvolvimento pessoal', 'position': 4, 'clicks': 950, 'impressions': 11000},
        {'keyword': 'rotina skincare iniciante', 'position': 6, 'clicks': 700, 'impressions': 9200},
        {'keyword': 'suplementos vitamina d', 'position': 8, 'clicks': 450, 'impressions': 6800},
        {'keyword': 'kindle vs tablet', 'position': 9, 'clicks': 380, 'impressions': 5500},
        {'keyword': 'livros infantis educativos', 'position': 2, 'clicks': 1400, 'impressions': 18000},
        {'keyword': 'protetor solar facial', 'position': 12, 'clicks': 320, 'impressions': 4200},
        {'keyword': 'whey protein isolado', 'position': 15, 'clicks': 250, 'impressions': 3100}
    ]
    
    seo_data = []
    
    for kw in keywords:
        ctr = kw['clicks'] / kw['impressions']
        seo_data.append({
            'keyword': kw['keyword'],
            'position': kw['position'],
            'clicks': kw['clicks'],
            'impressions': kw['impressions'],
            'ctr': ctr
        })
    
    return pd.DataFrame(seo_data)

@st.cache_data
def generate_traffic_sources():
    sources = [
        {'source': 'Google Organico', 'sessions': 8500, 'percentage': 68.2},
        {'source': 'Direto', 'sessions': 2100, 'percentage': 16.8},
        {'source': 'Facebook', 'sessions': 950, 'percentage': 7.6},
        {'source': 'Pinterest', 'sessions': 480, 'percentage': 3.8},
        {'source': 'Instagram', 'sessions': 320, 'percentage': 2.6},
        {'source': 'Outros', 'sessions': 150, 'percentage': 1.0}
    ]
    
    return pd.DataFrame(sources)

def main():
    st.markdown('<h1 class="main-header">📊 Dashboard PrimePickz</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #7f8c8d;">Analise de Performance do Blog de Afiliados Amazon</p>', unsafe_allow_html=True)
    
    traffic_data = generate_traffic_data()
    affiliate_data = generate_affiliate_data()
    content_data = generate_content_performance()
    seo_data = generate_seo_data()
    sources_data = generate_traffic_sources()
    
    st.sidebar.header("🔧 Filtros e Configuracoes")
    
    period_options = {
        "Ultimos 7 dias": 7,
        "Ultimos 30 dias": 30,
        "Ultimos 90 dias": 90,
        "Ultimos 6 meses": 180
    }
    
    selected_period = st.sidebar.selectbox(
        "📅 Periodo de Analise",
        options=list(period_options.keys()),
        index=1
    )
    
    days = period_options[selected_period]
    
    categories = ['Todas'] + list(content_data['category'].unique())
    selected_category = st.sidebar.selectbox(
        "📂 Categoria",
        options=categories
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Sobre o PrimePickz")
    st.sidebar.markdown("**Site:** primepickz.com.br")
    st.sidebar.markdown("**Tipo:** Blog de Afiliados Amazon")
    st.sidebar.markdown("**Tag Afiliado:** welldigital07-20")
    st.sidebar.markdown("**Categorias:** Beleza, Kindle, Livros, Saude e Bem Estar")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    traffic_filtered = traffic_data[traffic_data['date'] >= start_date]
    
    st.markdown('<div class="category-header">📈 Visao Geral - KPIs Principais</div>', unsafe_allow_html=True)
    
    total_visitors = traffic_filtered['visitors'].sum()
    total_pageviews = traffic_filtered['pageviews'].sum()
    avg_bounce_rate = traffic_filtered['bounce_rate'].mean()
    avg_session_duration = traffic_filtered['avg_session_duration'].mean()
    
    prev_start = start_date - timedelta(days=days)
    prev_traffic = traffic_data[(traffic_data['date'] >= prev_start) & (traffic_data['date'] < start_date)]
    
    if len(prev_traffic) > 0:
        prev_visitors = prev_traffic['visitors'].sum()
        visitors_change = ((total_visitors - prev_visitors) / prev_visitors * 100) if prev_visitors > 0 else 0
        
        prev_pageviews = prev_traffic['pageviews'].sum()
        pageviews_change = ((total_pageviews - prev_pageviews) / prev_pageviews * 100) if prev_pageviews > 0 else 0
    else:
        visitors_change = 0
        pageviews_change = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Visitantes Unicos",
            value=f"{total_visitors:,}",
            delta=f"{visitors_change:+.1f}%"
        )
    
    with col2:
        st.metric(
            label="📄 Pageviews",
            value=f"{total_pageviews:,}",
            delta=f"{pageviews_change:+.1f}%"
        )
    
    with col3:
        st.metric(
            label="⚡ Taxa de Rejeicao",
            value=f"{avg_bounce_rate:.1%}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="⏱️ Tempo Medio (min)",
            value=f"{avg_session_duration/60:.1f}",
            delta=None
        )
    
    st.markdown('<div class="category-header">📊 Evolucao do Trafego</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_traffic = px.line(
            traffic_filtered,
            x='date',
            y=['visitors', 'pageviews'],
            title="📈 Evolucao de Visitantes e Pageviews",
            labels={'value': 'Quantidade', 'date': 'Data', 'variable': 'Metrica'}
        )
        fig_traffic.update_layout(height=400)
        st.plotly_chart(fig_traffic, use_container_width=True)
    
    with col2:
        fig_sources = px.pie(
            sources_data,
            values='sessions',
            names='source',
            title="🌐 Fontes de Trafego"
        )
        fig_sources.update_layout(height=400)
        st.plotly_chart(fig_sources, use_container_width=True)
    
    st.markdown('<div class="category-header">💰 Analise de Afiliados Amazon</div>', unsafe_allow_html=True)
    
    total_clicks = affiliate_data['clicks'].sum()
    total_conversions = affiliate_data['conversions'].sum()
    total_commission = affiliate_data['commission_earned'].sum()
    avg_conversion_rate = affiliate_data['conversion_rate'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🖱️ Total de Cliques", f"{total_clicks:,}")
    
    with col2:
        st.metric("✅ Conversoes", f"{total_conversions:,}")
    
    with col3:
        st.metric("💵 Comissoes (R$)", f"{total_commission:,.2f}")
    
    with col4:
        st.metric("📊 Taxa de Conversao", f"{avg_conversion_rate:.2%}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_products = affiliate_data.nlargest(10, 'clicks')
        fig_products = px.bar(
            top_products,
            x='clicks',
            y='product_name',
            title="🏆 Top 10 Produtos por Cliques",
            orientation='h'
        )
        fig_products.update_layout(height=500)
        st.plotly_chart(fig_products, use_container_width=True)
    
    with col2:
        category_revenue = affiliate_data.groupby('category')['commission_earned'].sum().reset_index()
        fig_category = px.pie(
            category_revenue,
            values='commission_earned',
            names='category',
            title="💰 Receita por Categoria"
        )
        fig_category.update_layout(height=500)
        st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown('<div class="category-header">📝 Performance de Conteudo</div>', unsafe_allow_html=True)
    
    content_filtered = content_data.copy()
    if selected_category != 'Todas':
        content_filtered = content_filtered[content_filtered['category'] == selected_category]
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_posts = content_filtered.nlargest(8, 'pageviews')
        fig_posts = px.bar(
            top_posts,
            x='pageviews',
            y='title',
            title="📚 Top Posts por Pageviews",
            orientation='h',
            color='category'
        )
        fig_posts.update_layout(height=500)
        st.plotly_chart(fig_posts, use_container_width=True)
    
    with col2:
        category_performance = content_data.groupby('category').agg({
            'pageviews': 'sum',
            'affiliate_clicks': 'sum',
            'avg_time_on_page': 'mean'
        }).reset_index()
        
        fig_category_perf = px.scatter(
            category_performance,
            x='pageviews',
            y='affiliate_clicks',
            size='avg_time_on_page',
            color='category',
            title="🎯 Performance por Categoria",
            labels={
                'pageviews': 'Pageviews',
                'affiliate_clicks': 'Cliques em Afiliados',
                'avg_time_on_page': 'Tempo Medio na Pagina'
            }
        )
        fig_category_perf.update_layout(height=500)
        st.plotly_chart(fig_category_perf, use_container_width=True)
    
    st.markdown('<div class="category-header">🔍 SEO e Palavras-Chave</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_keywords = seo_data.nlargest(10, 'clicks')
        fig_keywords = px.bar(
            top_keywords,
            x='clicks',
            y='keyword',
            title="🔑 Top Keywords por Cliques",
            orientation='h'
        )
        fig_keywords.update_layout(height=500)
        st.plotly_chart(fig_keywords, use_container_width=True)
    
    with col2:
        fig_position = px.scatter(
            seo_data,
            x='position',
            y='ctr',
            size='impressions',
            hover_data=['keyword'],
            title="📍 Posicao vs CTR",
            labels={
                'position': 'Posicao no Google',
                'ctr': 'Taxa de Cliques (CTR)',
                'impressions': 'Impressoes'
            }
        )
        fig_position.update_layout(height=500)
        st.plotly_chart(fig_position, use_container_width=True)
    
    st.markdown('<div class="category-header">💡 Insights e Recomendacoes</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Principais Insights")
        
        best_category = affiliate_data.groupby('category')['commission_earned'].sum().idxmax()
        best_product = affiliate_data.loc[affiliate_data['commission_earned'].idxmax(), 'product_name']
        best_post = content_data.loc[content_data['pageviews'].idxmax(), 'title']
        
        st.success(f"✅ **Melhor categoria:** {best_category}")
        st.info(f"🏆 **Produto top:** {best_product}")
        st.info(f"📚 **Post mais visitado:** {best_post}")
        
        recent_traffic = traffic_filtered.tail(7)['visitors'].mean()
        older_traffic = traffic_filtered.head(7)['visitors'].mean()
        
        if recent_traffic > older_traffic:
            st.success("📈 **Tendencia:** Trafego em crescimento!")
        else:
            st.warning("📉 **Atencao:** Trafego em declinio")
    
    with col2:
        st.subheader("🚀 Recomendacoes")
        
        st.markdown("""
        **Para aumentar receita:**
        - Focar mais conteudo na categoria de melhor performance
        - Otimizar posts com alta taxa de rejeicao
        - Criar mais conteudo sobre produtos top
        
        **Para melhorar SEO:**
        - Trabalhar keywords em posicoes 4-10
        - Criar conteudo para keywords de alto volume
        - Otimizar titulos e meta descriptions
        
        **Para engajamento:**
        - Aumentar tempo na pagina com conteudo mais rico
        - Adicionar mais CTAs nos posts populares
        - Melhorar experiencia mobile
        """)
    
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d;">Dashboard PrimePickz - Desenvolvido com Streamlit | Dados atualizados em tempo real</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

