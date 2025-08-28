# Instruções de Deploy - Dashboard PrimePickz

## 🚀 Deploy no Streamlit Community Cloud (GRATUITO)

### Pré-requisitos
- Conta no GitHub
- Conta no Streamlit Cloud (gratuita)

### Passo 1: Preparar Repositório GitHub

1. **Criar novo repositório no GitHub**
   - Nome sugerido: `dashboard-primepickz`
   - Visibilidade: Público (para deploy gratuito)

2. **Fazer upload dos arquivos**
   ```
   dashboard-primepickz/
   ├── dashboard.py
   ├── data_generator.py
   ├── requirements.txt
   └── README.md
   ```

3. **Verificar estrutura**
   - `dashboard.py` deve estar na raiz
   - `requirements.txt` deve listar todas as dependências
   - Arquivos devem estar commitados

### Passo 2: Deploy no Streamlit Cloud

1. **Acessar Streamlit Cloud**
   - Ir para: https://share.streamlit.io
   - Fazer login com GitHub

2. **Criar nova aplicação**
   - Clicar em "New app"
   - Selecionar repositório: `dashboard-primepickz`
   - Branch: `main`
   - Main file path: `dashboard.py`

3. **Configurações avançadas (opcional)**
   - Python version: `3.11`
   - Secrets: Não necessário para dados simulados

4. **Deploy**
   - Clicar em "Deploy!"
   - Aguardar build (2-5 minutos)

### Passo 3: Verificar Deploy

1. **URL da aplicação**
   - Será gerada automaticamente
   - Formato: `https://[app-name]-[random].streamlit.app`

2. **Testar funcionalidades**
   - Verificar carregamento dos gráficos
   - Testar filtros de período e categoria
   - Confirmar responsividade

## 🔧 Deploy Local (Desenvolvimento)

### Instalação
```bash
# Clonar repositório
git clone https://github.com/[usuario]/dashboard-primepickz.git
cd dashboard-primepickz

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run dashboard.py
```

### Acesso Local
- URL: http://localhost:8501
- Hot reload: Ativado automaticamente

## 🔄 Atualizações e Manutenção

### Atualizar Dashboard
1. Fazer alterações nos arquivos
2. Commit e push para GitHub
3. Deploy automático no Streamlit Cloud

### Monitoramento
- Logs disponíveis no painel Streamlit Cloud
- Métricas de uso na dashboard do Streamlit
- Alertas automáticos em caso de erro

## 🔐 Configurações de Segurança

### Dados Simulados (Atual)
- Não requer configurações especiais
- Dados gerados dinamicamente
- Sem informações sensíveis

### Dados Reais (Futuro)
- Usar Streamlit Secrets para APIs
- Configurar variáveis de ambiente
- Implementar autenticação se necessário

## 📊 Integrações com Dados Reais

### Google Analytics 4
```python
# Adicionar ao requirements.txt
google-analytics-data==0.17.1

# Configurar secrets no Streamlit Cloud
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

### Google Search Console
```python
# Adicionar ao requirements.txt
google-api-python-client==2.108.0

# Configurar autenticação OAuth2
# Usar Streamlit Secrets para credenciais
```

### Amazon Associates API
```python
# Adicionar ao requirements.txt
python-amazon-paapi==5.1.1

# Configurar secrets
[amazon_api]
access_key = "your-access-key"
secret_key = "your-secret-key"
partner_tag = "welldigital25-20"
host = "webservices.amazon.com.br"
region = "us-east-1"
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de dependências**
   - Verificar `requirements.txt`
   - Usar versões específicas
   - Testar localmente primeiro

2. **Timeout no deploy**
   - Reduzir tamanho dos dados
   - Otimizar imports
   - Usar cache do Streamlit

3. **Erro de memória**
   - Implementar paginação
   - Usar lazy loading
   - Otimizar DataFrames

### Logs e Debug
```python
# Adicionar logging ao dashboard.py
import logging
logging.basicConfig(level=logging.INFO)

# Usar st.error() para debug
st.error("Debug info here")
```

## 📈 Otimizações de Performance

### Cache de Dados
```python
@st.cache_data
def load_data():
    # Função já implementada
    return data
```

### Lazy Loading
```python
# Carregar dados apenas quando necessário
if st.button("Carregar dados"):
    data = load_heavy_data()
```

### Compressão
```python
# Usar formatos eficientes
df.to_parquet('data.parquet')  # Ao invés de CSV
```

## 🔮 Roadmap de Melhorias

### Versão 2.0
- [ ] Integração com Google Analytics
- [ ] Dados reais de afiliados Amazon
- [ ] Alertas automáticos
- [ ] Export para PDF

### Versão 3.0
- [ ] Machine Learning para previsões
- [ ] Comparação com concorrentes
- [ ] Dashboard mobile nativo
- [ ] API própria para dados

## 📞 Suporte Técnico

### Recursos Úteis
- **Documentação Streamlit**: https://docs.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Para bugs específicos

### Contato
- **Dashboard**: Desenvolvido para PrimePickz.com.br
- **Suporte**: Via issues no repositório GitHub

---

*Instruções atualizadas para deploy no Streamlit Community Cloud*

