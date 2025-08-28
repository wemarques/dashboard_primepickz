import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_traffic_data():
    """Gera dados simulados de tráfego para os últimos 6 meses"""
    
    # Gerar datas dos últimos 6 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Simular dados de tráfego com sazonalidade
    traffic_data = []
    base_visitors = 1200
    
    for date in dates:
        # Adicionar sazonalidade (fins de semana menores, feriados maiores)
        day_of_week = date.weekday()
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        
        # Crescimento gradual ao longo do tempo
        growth_factor = 1 + (date - start_date).days * 0.002
        
        # Variação aleatória
        random_factor = np.random.normal(1, 0.15)
        
        visitors = int(base_visitors * weekend_factor * growth_factor * random_factor)
        pageviews = int(visitors * np.random.uniform(2.1, 3.8))
        bounce_rate = np.random.uniform(0.35, 0.65)
        avg_session_duration = np.random.uniform(120, 300)  # segundos
        
        traffic_data.append({
            'date': date,
            'visitors': max(visitors, 100),
            'pageviews': max(pageviews, 200),
            'bounce_rate': bounce_rate,
            'avg_session_duration': avg_session_duration,
            'sessions': int(visitors * np.random.uniform(1.1, 1.4))
        })
    
    return pd.DataFrame(traffic_data)

def generate_affiliate_data():
    """Gera dados simulados de afiliados Amazon"""
    
    products = [
        {'name': 'iPhone 15 Pro', 'category': 'Eletrônicos', 'commission_rate': 0.02},
        {'name': 'Creme Facial Neutrogena', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Kindle Paperwhite', 'category': 'Kindle', 'commission_rate': 0.04},
        {'name': 'Livro: Hábitos Atômicos', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Whey Protein', 'category': 'Saúde & Bem Estar', 'commission_rate': 0.05},
        {'name': 'MacBook Air M3', 'category': 'Eletrônicos', 'commission_rate': 0.02},
        {'name': 'Sérum Vitamina C', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Kindle Oasis', 'category': 'Kindle', 'commission_rate': 0.04},
        {'name': 'Livro: O Poder do Hábito', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Ômega 3', 'category': 'Saúde & Bem Estar', 'commission_rate': 0.05},
        {'name': 'AirPods Pro', 'category': 'Eletrônicos', 'commission_rate': 0.02},
        {'name': 'Base Líquida Maybelline', 'category': 'Beleza', 'commission_rate': 0.08},
        {'name': 'Livro: Mindset', 'category': 'Livros', 'commission_rate': 0.06},
        {'name': 'Colágeno Hidrolisado', 'category': 'Saúde & Bem Estar', 'commission_rate': 0.05},
        {'name': 'iPad Air', 'category': 'Eletrônicos', 'commission_rate': 0.02}
    ]
    
    affiliate_data = []
    
    for product in products:
        # Simular dados dos últimos 30 dias
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

def generate_content_performance():
    """Gera dados de performance de conteúdo por categoria"""
    
    posts = [
        {'title': '12 Livros que Mudam a Vida', 'category': 'Livros', 'publish_date': '2024-08-26'},
        {'title': 'Proteção Solar no Nordeste', 'category': 'Beleza', 'publish_date': '2024-08-26'},
        {'title': 'Kindle vs Paperwhite 2024', 'category': 'Kindle', 'publish_date': '2024-08-21'},
        {'title': 'Importância da Leitura Infantil', 'category': 'Livros', 'publish_date': '2024-08-24'},
        {'title': 'Cuidados com Pele Seca', 'category': 'Beleza', 'publish_date': '2024-08-21'},
        {'title': 'Melhores Livros Infantis 2024', 'category': 'Livros', 'publish_date': '2024-08-19'},
        {'title': 'Rotina Skincare Perfeita', 'category': 'Beleza', 'publish_date': '2024-08-18'},
        {'title': 'Achados de Beleza', 'category': 'Beleza', 'publish_date': '2024-08-06'},
        {'title': 'Suplementos para Imunidade', 'category': 'Saúde & Bem Estar', 'publish_date': '2024-08-15'},
        {'title': 'Kindle Unlimited Vale a Pena?', 'category': 'Kindle', 'publish_date': '2024-08-10'}
    ]
    
    content_data = []
    
    for post in posts:
        pageviews = np.random.randint(800, 5000)
        avg_time_on_page = np.random.uniform(180, 420)  # segundos
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

def generate_seo_data():
    """Gera dados simulados de SEO"""
    
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

def generate_traffic_sources():
    """Gera dados de fontes de tráfego"""
    
    sources = [
        {'source': 'Google Orgânico', 'sessions': 8500, 'percentage': 68.2},
        {'source': 'Direto', 'sessions': 2100, 'percentage': 16.8},
        {'source': 'Facebook', 'sessions': 950, 'percentage': 7.6},
        {'source': 'Pinterest', 'sessions': 480, 'percentage': 3.8},
        {'source': 'Instagram', 'sessions': 320, 'percentage': 2.6},
        {'source': 'Outros', 'sessions': 150, 'percentage': 1.0}
    ]
    
    return pd.DataFrame(sources)

if __name__ == "__main__":
    # Teste das funções
    print("Gerando dados de teste...")
    
    traffic = generate_traffic_data()
    print(f"Dados de tráfego: {len(traffic)} registros")
    
    affiliate = generate_affiliate_data()
    print(f"Dados de afiliados: {len(affiliate)} registros")
    
    content = generate_content_performance()
    print(f"Dados de conteúdo: {len(content)} registros")
    
    seo = generate_seo_data()
    print(f"Dados de SEO: {len(seo)} registros")
    
    sources = generate_traffic_sources()
    print(f"Dados de fontes: {len(sources)} registros")

