import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import altair as alt

# Importar gerador de dados
from data_generator import (
    generate_traffic_data,
    generate_affiliate_data,
    generate_content_performance,
    generate_seo_data,
    generate_traffic_sources
)

# Configuração da página
st.set_page_config(
    page_title="Dashboard PrimePickz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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

# Cache dos dados
@st.cache_data
def load_data():
    """Carrega todos os dados necessários"""
    return {
        'traffic': generate_traffic_data(),
        'affiliate': generate_affiliate_data(),
        'content': generate_content_performance(),
        'seo': generate_seo_data(),
        'sources': generate_traffic_sources()
    }

def main():
    # Header principal
    st.markdown('<h1 class="main-header">📊 Dashboard PrimePickz</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #7f8c8d;">Análise de Performance do Blog de Afiliados Amazon</p>', unsafe_allow_html=True)
    
    # Carregar dados
    data = load_data()
    
    # Sidebar com filtros
    st.sidebar.header("🔧 Filtros e Configurações")
    
    # Filtro de período
    period_options = {
        "Últimos 7 dias": 7,
        "Últimos 30 dias": 30,
        "Últimos 90 dias": 90,
        "Últimos 6 meses": 180
    }
    
    selected_period = st.sidebar.selectbox(
        "📅 Período de Análise",
        options=list(period_options.keys()),
        index=1
    )
    
    days = period_options[selected_period]
    
    # Filtro de categoria
    categories = ['Todas'] + list(data['content']['category'].unique())
    selected_category = st.sidebar.selectbox(
        "📂 Categoria",
        options=categories
    )
    
    # Informações do site
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Sobre o PrimePickz")
    st.sidebar.markdown("**Site:** primepickz.com.br")
    st.sidebar.markdown("**Tipo:** Blog de Afiliados Amazon")
    st.sidebar.markdown("**Tag Afiliado:** welldigital25-20")
    st.sidebar.markdown("**Categorias:** Beleza, Kindle, Livros, Saúde & Bem Estar")
    
    # Filtrar dados por período
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    traffic_filtered = data['traffic'][data['traffic']['date'] >= start_date]
    
    # 1. VISÃO GERAL - KPIs
    st.markdown('<div class="category-header">📈 Visão Geral - KPIs Principais</div>', unsafe_allow_html=True)
    
    # Calcular métricas
    total_visitors = traffic_filtered['visitors'].sum()
    total_pageviews = traffic_filtered['pageviews'].sum()
    avg_bounce_rate = traffic_filtered['bounce_rate'].mean()
    avg_session_duration = traffic_filtered['avg_session_duration'].mean()
    
    # Calcular variação (comparar com período anterior)
    prev_start = start_date - timedelta(days=days)
    prev_traffic = data['traffic'][(data['traffic']['date'] >= prev_start) & (data['traffic']['date'] < start_date)]
    
    if len(prev_traffic) > 0:
        prev_visitors = prev_traffic['visitors'].sum()
        visitors_change = ((total_visitors - prev_visitors) / prev_visitors * 100) if prev_visitors > 0 else 0
        
        prev_pageviews = prev_traffic['pageviews'].sum()
        pageviews_change = ((total_pageviews - prev_pageviews) / prev_pageviews * 100) if prev_pageviews > 0 else 0
    else:
        visitors_change = 0
        pageviews_change = 0
    
    # Exibir KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Visitantes Únicos",
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
            label="⚡ Taxa de Rejeição",
            value=f"{avg_bounce_rate:.1%}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="⏱️ Tempo Médio (min)",
            value=f"{avg_session_duration/60:.1f}",
            delta=None
        )
    
    # 2. GRÁFICOS DE TRÁFEGO
    st.markdown('<div class="category-header">📊 Evolução do Tráfego</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de evolução temporal
        fig_traffic = px.line(
            traffic_filtered,
            x='date',
            y=['visitors', 'pageviews'],
            title="📈 Evolução de Visitantes e Pageviews",
            labels={'value': 'Quantidade', 'date': 'Data', 'variable': 'Métrica'}
        )
        fig_traffic.update_layout(height=400)
        st.plotly_chart(fig_traffic, use_container_width=True)
    
    with col2:
        # Gráfico de fontes de tráfego
        fig_sources = px.pie(
            data['sources'],
            values='sessions',
            names='source',
            title="🌐 Fontes de Tráfego"
        )
        fig_sources.update_layout(height=400)
        st.plotly_chart(fig_sources, use_container_width=True)
    
    # 3. ANÁLISE DE AFILIADOS AMAZON
    st.markdown('<div class="category-header">💰 Análise de Afiliados Amazon</div>', unsafe_allow_html=True)
    
    # KPIs de afiliados
    total_clicks = data['affiliate']['clicks'].sum()
    total_conversions = data['affiliate']['conversions'].sum()
    total_commission = data['affiliate']['commission_earned'].sum()
    avg_conversion_rate = data['affiliate']['conversion_rate'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🖱️ Total de Cliques", f"{total_clicks:,}")
    
    with col2:
        st.metric("✅ Conversões", f"{total_conversions:,}")
    
    with col3:
        st.metric("💵 Comissões (R$)", f"{total_commission:,.2f}")
    
    with col4:
        st.metric("📊 Taxa de Conversão", f"{avg_conversion_rate:.2%}")
    
    # Gráficos de afiliados
    col1, col2 = st.columns(2)
    
    with col1:
        # Top produtos por cliques
        top_products = data['affiliate'].nlargest(10, 'clicks')
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
        # Receita por categoria
        category_revenue = data['affiliate'].groupby('category')['commission_earned'].sum().reset_index()
        fig_category = px.pie(
            category_revenue,
            values='commission_earned',
            names='category',
            title="💰 Receita por Categoria"
        )
        fig_category.update_layout(height=500)
        st.plotly_chart(fig_category, use_container_width=True)
    
    # 4. PERFORMANCE DE CONTEÚDO
    st.markdown('<div class="category-header">📝 Performance de Conteúdo</div>', unsafe_allow_html=True)
    
    # Filtrar conteúdo por categoria se selecionada
    content_data = data['content'].copy()
    if selected_category != 'Todas':
        content_data = content_data[content_data['category'] == selected_category]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top posts por pageviews
        top_posts = content_data.nlargest(8, 'pageviews')
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
        # Performance por categoria
        category_performance = data['content'].groupby('category').agg({
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
                'avg_time_on_page': 'Tempo Médio na Página'
            }
        )
        fig_category_perf.update_layout(height=500)
        st.plotly_chart(fig_category_perf, use_container_width=True)
    
    # 5. SEO E PALAVRAS-CHAVE
    st.markdown('<div class="category-header">🔍 SEO e Palavras-Chave</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top keywords por cliques
        top_keywords = data['seo'].nlargest(10, 'clicks')
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
        # Posição vs CTR
        fig_position = px.scatter(
            data['seo'],
            x='position',
            y='ctr',
            size='impressions',
            hover_data=['keyword'],
            title="📍 Posição vs CTR",
            labels={
                'position': 'Posição no Google',
                'ctr': 'Taxa de Cliques (CTR)',
                'impressions': 'Impressões'
            }
        )
        fig_position.update_layout(height=500)
        st.plotly_chart(fig_position, use_container_width=True)
    
    # 6. TABELAS DETALHADAS
    st.markdown('<div class="category-header">📋 Dados Detalhados</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🛍️ Produtos Afiliados", "📝 Conteúdo", "🔍 SEO"])
    
    with tab1:
        st.subheader("Produtos com Melhor Performance")
        affiliate_display = data['affiliate'].copy()
        affiliate_display['commission_earned'] = affiliate_display['commission_earned'].apply(lambda x: f"R$ {x:,.2f}")
        affiliate_display['conversion_rate'] = affiliate_display['conversion_rate'].apply(lambda x: f"{x:.2%}")
        st.dataframe(
            affiliate_display[['product_name', 'category', 'clicks', 'conversions', 'conversion_rate', 'commission_earned']],
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Performance de Posts")
        content_display = content_data.copy()
        content_display['avg_time_on_page'] = content_display['avg_time_on_page'].apply(lambda x: f"{x/60:.1f} min")
        content_display['bounce_rate'] = content_display['bounce_rate'].apply(lambda x: f"{x:.1%}")
        st.dataframe(
            content_display[['title', 'category', 'pageviews', 'avg_time_on_page', 'bounce_rate', 'affiliate_clicks']],
            use_container_width=True
        )
    
    with tab3:
        st.subheader("Keywords e Posições")
        seo_display = data['seo'].copy()
        seo_display['ctr'] = seo_display['ctr'].apply(lambda x: f"{x:.2%}")
        st.dataframe(
            seo_display[['keyword', 'position', 'clicks', 'impressions', 'ctr']],
            use_container_width=True
        )
    
    # 7. INSIGHTS E RECOMENDAÇÕES
    st.markdown('<div class="category-header">💡 Insights e Recomendações</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Principais Insights")
        
        # Calcular insights automáticos
        best_category = data['affiliate'].groupby('category')['commission_earned'].sum().idxmax()
        best_product = data['affiliate'].loc[data['affiliate']['commission_earned'].idxmax(), 'product_name']
        best_post = data['content'].loc[data['content']['pageviews'].idxmax(), 'title']
        
        st.success(f"✅ **Melhor categoria:** {best_category}")
        st.info(f"🏆 **Produto top:** {best_product}")
        st.info(f"📚 **Post mais visitado:** {best_post}")
        
        # Análise de tendências
        recent_traffic = traffic_filtered.tail(7)['visitors'].mean()
        older_traffic = traffic_filtered.head(7)['visitors'].mean()
        
        if recent_traffic > older_traffic:
            st.success("📈 **Tendência:** Tráfego em crescimento!")
        else:
            st.warning("📉 **Atenção:** Tráfego em declínio")
    
    with col2:
        st.subheader("🚀 Recomendações")
        
        st.markdown("""
        **Para aumentar receita:**
        - Focar mais conteúdo na categoria de melhor performance
        - Otimizar posts com alta taxa de rejeição
        - Criar mais conteúdo sobre produtos top
        
        **Para melhorar SEO:**
        - Trabalhar keywords em posições 4-10
        - Criar conteúdo para keywords de alto volume
        - Otimizar títulos e meta descriptions
        
        **Para engajamento:**
        - Aumentar tempo na página com conteúdo mais rico
        - Adicionar mais CTAs nos posts populares
        - Melhorar experiência mobile
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d;">Dashboard PrimePickz - Desenvolvido com Streamlit | Dados atualizados em tempo real</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

