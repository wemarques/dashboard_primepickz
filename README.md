# Dashboard PrimePickz - Análise de Performance

Dashboard completo em Streamlit para análise de performance do blog de afiliados Amazon **PrimePickz.com.br**.

## 🎯 Funcionalidades

### 📊 Visão Geral
- **KPIs Principais**: Visitantes únicos, pageviews, taxa de rejeição, tempo médio
- **Evolução Temporal**: Gráficos de linha com dados dos últimos 6 meses
- **Fontes de Tráfego**: Distribuição por canal (Google, Direto, Redes Sociais)
- **Comparação de Períodos**: Variação percentual vs período anterior

### 💰 Análise de Afiliados Amazon
- **Métricas de Conversão**: Cliques, conversões, comissões, taxa de conversão
- **Top Produtos**: Ranking por cliques e receita
- **Performance por Categoria**: Beleza, Kindle, Livros, Saúde & Bem Estar
- **Tag de Afiliado**: welldigital25-20 (integrada)

### 📝 Performance de Conteúdo
- **Top Posts**: Ranking por pageviews e engajamento
- **Análise por Categoria**: Performance específica de cada nicho
- **Métricas de Engajamento**: Tempo na página, cliques em afiliados
- **Correlação**: Pageviews vs cliques em produtos

### 🔍 SEO e Palavras-Chave
- **Top Keywords**: Ranking por cliques e impressões
- **Análise de Posições**: Posição no Google vs CTR
- **Oportunidades**: Keywords para otimização

### 💡 Insights Automáticos
- **Identificação Automática**: Melhor categoria, produto top, post mais visitado
- **Tendências**: Análise de crescimento/declínio
- **Recomendações**: Sugestões acionáveis baseadas em dados

## 🛠 Tecnologias Utilizadas

- **Streamlit**: Framework web para Python
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Gráficos interativos
- **NumPy**: Computação numérica
- **Python 3.11**: Linguagem base

## 📁 Estrutura do Projeto

```
dashboard_primepickz/
├── dashboard.py          # Aplicação principal Streamlit
├── data_generator.py     # Gerador de dados simulados
├── requirements.txt      # Dependências do projeto
└── README.md            # Documentação
```

## 🚀 Como Executar Localmente

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Dashboard
```bash
streamlit run dashboard.py
```

### 3. Acessar no Navegador
```
http://localhost:8501
```

## ☁️ Deploy no Streamlit Community Cloud

### 1. Preparar Repositório
- Fazer upload dos arquivos para um repositório GitHub
- Garantir que `requirements.txt` está presente
- Verificar se `dashboard.py` está na raiz

### 2. Deploy no Streamlit Cloud
1. Acessar [share.streamlit.io](https://share.streamlit.io)
2. Conectar conta GitHub
3. Selecionar repositório
4. Definir arquivo principal: `dashboard.py`
5. Fazer deploy

### 3. Configurações Recomendadas
- **Python Version**: 3.11
- **Main File**: dashboard.py
- **Requirements**: requirements.txt

## 📊 Dados Simulados

O dashboard utiliza dados simulados realistas que incluem:

### Tráfego (6 meses)
- Visitantes únicos diários
- Pageviews com sazonalidade
- Taxa de rejeição variável
- Tempo médio de sessão

### Afiliados Amazon
- 15 produtos em 5 categorias
- Cliques, conversões e comissões
- Taxas de conversão realistas
- Produtos baseados no PrimePickz

### Conteúdo
- 10 posts recentes
- Performance por categoria
- Métricas de engajamento
- Cliques em links de afiliados

### SEO
- 10 palavras-chave principais
- Posições no Google
- Impressões e cliques
- CTR por keyword

## 🔧 Filtros Interativos

### Período de Análise
- Últimos 7 dias
- Últimos 30 dias
- Últimos 90 dias
- Últimos 6 meses

### Categoria
- Todas
- Beleza
- Kindle
- Livros
- Saúde & Bem Estar

## 📈 Métricas Principais

### KPIs de Tráfego
- **Visitantes Únicos**: Total de usuários únicos
- **Pageviews**: Total de páginas visualizadas
- **Taxa de Rejeição**: % de sessões com uma única página
- **Tempo Médio**: Duração média das sessões

### KPIs de Afiliados
- **Total de Cliques**: Cliques em links de afiliados
- **Conversões**: Compras realizadas
- **Comissões**: Receita gerada
- **Taxa de Conversão**: % de cliques que convertem

## 🎨 Interface

### Layout Responsivo
- Sidebar com filtros e informações
- Grid de KPIs em destaque
- Gráficos organizados em colunas
- Tabelas detalhadas em abas

### Cores e Estilo
- Paleta azul profissional
- Ícones intuitivos
- Tipografia clara
- Hover effects nos gráficos

## 🔮 Integrações Futuras

### APIs Reais
- **Google Analytics 4**: Dados de tráfego reais
- **Google Search Console**: Métricas de SEO
- **Amazon Associates API**: Dados de conversão
- **Social Media APIs**: Métricas de redes sociais

### Funcionalidades Avançadas
- **Alertas Automáticos**: Notificações de mudanças significativas
- **Relatórios PDF**: Export automático
- **Previsões**: Machine learning para tendências
- **Comparação de Concorrentes**: Benchmarking

## 📞 Suporte

Para dúvidas ou sugestões sobre o dashboard:
- **Site**: primepickz.com.br
- **Tipo**: Blog de Afiliados Amazon
- **Categorias**: Beleza, Kindle, Livros, Saúde & Bem Estar

## 📄 Licença

Este projeto foi desenvolvido especificamente para o PrimePickz.com.br.

---

*Dashboard desenvolvido com Streamlit | Dados atualizados em tempo real*

