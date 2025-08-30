import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import PyPDF2
import io
import re
import hashlib
from datetime import datetime, date
import calendar
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro Automatizado",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminho do banco de dados
DB_PATH = 'financeiro.db'

# Códigos específicos para créditos (conforme regra de negócio)
CODIGOS_CREDITO = ['2002', '2007', '2043', '2045', '2049', '2116', '2186', '21100']

# Inicialização do banco de dados
def init_database():
    """Inicializa o banco de dados SQLite com tratamento de erro"""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        cursor = conn.cursor()
        
        # Configurações SQLite para melhor performance
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=memory")
        
        # Tabela de transações (despesas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                estabelecimento TEXT NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL,
                cartao TEXT NOT NULL,
                arquivo_origem TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de receitas (agora com código para controle)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                descricao TEXT NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL,
                fonte TEXT NOT NULL,
                codigo TEXT,
                tipo_lancamento TEXT DEFAULT 'credito',
                arquivo_origem TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de arquivos processados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arquivos_processados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT UNIQUE NOT NULL,
                hash_arquivo TEXT NOT NULL,
                tipo_arquivo TEXT NOT NULL,
                data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_transacoes INTEGER DEFAULT 0
            )
        ''')
        
        # Adicionar colunas se não existirem (para compatibilidade)
        try:
            cursor.execute("ALTER TABLE receitas ADD COLUMN codigo TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE receitas ADD COLUMN tipo_lancamento TEXT DEFAULT 'credito'")
        except:
            pass
        
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"Erro ao inicializar banco de dados: {e}")
        return None

def get_db_connection():
    """Obtém uma nova conexão com o banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com banco de dados: {e}")
        return None

# Funções auxiliares
def calcular_hash_arquivo(file_bytes):
    """Calcula hash MD5 do arquivo"""
    return hashlib.md5(file_bytes).hexdigest()

def extrair_texto_pdf(file_bytes):
    """Extrai texto do PDF com melhor tratamento de erros"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        texto = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    texto += page_text + "\n"
            except Exception as e:
                st.warning(f"Erro ao extrair texto da página {page_num + 1}: {e}")
                continue
        return texto
    except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")
        return ""

def debug_texto_extraido(texto, max_chars=500):
    """Mostra preview do texto extraído para debug"""
    if texto:
        preview = texto[:max_chars] + "..." if len(texto) > max_chars else texto
        st.text_area("🔍 Texto extraído do PDF (preview):", preview, height=150)
        st.info(f"📄 Total de caracteres extraídos: {len(texto)}")
        return True
    else:
        st.error("❌ Nenhum texto foi extraído do PDF")
        return False

def categorizar_estabelecimento(estabelecimento):
    """Categoriza automaticamente baseado no nome do estabelecimento"""
    estabelecimento = estabelecimento.upper()
    
    categorias = {
        'Alimentação': [
            'SUPERMERCADO', 'PADARIA', 'MERCADO', 'HORTIFRUTI', 'ACOUGUE', 'FEIRA', 
            'EMPORIO', 'ATACADAO', 'EXTRA', 'CARREFOUR', 'WALMART', 'BIG', 'ASSAI'
        ],
        'Restaurante': [
            'RESTAURANTE', 'MCDONALDS', 'SUBWAY', 'IFOOD', 'UBER EATS', 'BURGUER', 
            'PIZZA', 'LANCHONETE', 'BAR', 'CAFE', 'CAFETERIA', 'DELIVERY', 'FOOD',
            'OUTBACK', 'SPOLETO', 'HABIB', 'GIRAFFAS', 'BOBS'
        ],
        'Transporte': [
            'UBER', '99', 'POSTO', 'PETROBRAS', 'SHELL', 'ESTACIONAMENTO', 'PEDAGIO', 
            'METRO', 'ONIBUS', 'TAXI', 'COMBUSTIVEL', 'GASOLINA', 'ALCOOL', 'DIESEL'
        ],
        'Lazer': [
            'CINEMA', 'NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'SHOPPING', 'LIVRARIA', 
            'TEATRO', 'PARQUE', 'CLUBE', 'YOUTUBE', 'DISNEY', 'GLOBOPLAY'
        ],
        'Saúde': [
            'FARMACIA', 'DROGA', 'DROGASIL', 'CLINICA', 'LABORATORIO', 'DENTISTA', 
            'HOSPITAL', 'MEDICO', 'ULTRAFARMA', 'PACHECO', 'RAIA'
        ],
        'Vestuário': [
            'ZARA', 'C&A', 'RENNER', 'NIKE', 'ADIDAS', 'ROUPA', 'CALCADO', 'SAPATO', 
            'TENIS', 'RIACHUELO', 'MARISA', 'LOJAS AMERICANAS'
        ],
        'Casa': [
            'LEROY MERLIN', 'CASAS BAHIA', 'AMERICANAS', 'MOVEIS', 'DECORACAO', 
            'CONSTRUCAO', 'MAGAZINE LUIZA', 'PONTO FRIO', 'FAST SHOP'
        ],
        'Educação': [
            'LIVRARIA', 'CURSO', 'UNIVERSIDADE', 'MATERIAL ESCOLAR', 'ESCOLA', 
            'FACULDADE', 'LIVRO', 'SARAIVA', 'CULTURA'
        ],
        'Serviços': [
            'CLARO', 'VIVO', 'TIM', 'CONTA', 'SEGURO', 'INTERNET', 'BANCO', 
            'CARTORIO', 'CORREIOS', 'OI', 'SKY', 'NET'
        ]
    }
    
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra in estabelecimento:
                return categoria
    
    return 'Outros'

def detectar_cartao(nome_arquivo, texto):
    """Detecta o cartão baseado no nome do arquivo e conteúdo"""
    nome_lower = nome_arquivo.lower()
    texto_lower = texto.lower()
    
    if 'azul' in nome_lower or 'azul' in texto_lower:
        return 'Azul'
    elif 'santander' in nome_lower or 'santander' in texto_lower:
        return 'Santander'
    elif 'samsung' in nome_lower or 'samsung' in texto_lower:
        return 'Samsung'
    elif 'caixa' in nome_lower or 'caixa' in texto_lower:
        if 'elo' in nome_lower or 'elo' in texto_lower:
            return 'Caixa Elo'
        elif 'visa' in nome_lower or 'visa' in texto_lower:
            return 'Caixa Visa'
        else:
            return 'Caixa'
    elif 'visa' in nome_lower or 'visa' in texto_lower:
        return 'Visa'
    elif 'mastercard' in nome_lower or 'mastercard' in texto_lower:
        return 'Mastercard'
    else:
        return 'Cartão'

def converter_data(data_str):
    """Converte string de data para objeto date com correção de ano"""
    try:
        # Limpar a string
        data_str = data_str.strip()
        
        # Tentar diferentes formatos
        formatos = [
            '%d/%m/%Y',
            '%d/%m/%y',
            '%d/%m',
            '%d-%m-%Y',
            '%d-%m-%y',
            '%d-%m'
        ]
        
        for formato in formatos:
            try:
                if formato.endswith('/%m') or formato.endswith('-%m'):
                    # Adicionar ano atual se não especificado
                    ano_atual = datetime.now().year
                    data_str_completa = f"{data_str}/{ano_atual}"
                    data_obj = datetime.strptime(data_str_completa, formato + f'/{ano_atual}').date()
                elif formato.endswith('/%y') or formato.endswith('-%y'):
                    # Corrigir interpretação de anos de 2 dígitos
                    data_obj = datetime.strptime(data_str, formato).date()
                    
                    # Se o ano for menor que 1950, assumir que é 20XX
                    if data_obj.year < 1950:
                        data_obj = data_obj.replace(year=data_obj.year + 100)
                    # Se o ano for maior que ano atual + 10, assumir que é 19XX
                    elif data_obj.year > datetime.now().year + 10:
                        data_obj = data_obj.replace(year=data_obj.year - 100)
                else:
                    data_obj = datetime.strptime(data_str, formato).date()
                
                # Verificar se a data é razoável (não muito antiga ou futura)
                ano_atual = datetime.now().year
                if data_obj.year < 2020 or data_obj.year > ano_atual + 2:
                    continue
                
                return data_obj
            except ValueError:
                continue
        
        return None
    except Exception:
        return None

def converter_valor(valor_str):
    """Converte string de valor para float"""
    try:
        # Limpar a string
        valor_str = valor_str.strip()
        valor_str = valor_str.replace('R$', '').replace('$', '')
        valor_str = valor_str.replace(' ', '')
        
        # Converter vírgula para ponto (formato brasileiro)
        if ',' in valor_str and '.' in valor_str:
            # Formato: 1.234,56
            valor_str = valor_str.replace('.', '').replace(',', '.')
        elif ',' in valor_str:
            # Formato: 1234,56
            valor_str = valor_str.replace(',', '.')
        
        valor = float(valor_str)
        
        # Verificar se o valor é razoável
        if valor < 0.01 or valor > 100000:
            return 0
        
        return valor
    except Exception:
        return 0

def classificar_lancamento_por_codigo(codigo):
    """Classifica lançamento como crédito ou débito baseado nas regras específicas"""
    codigo_str = str(codigo).strip()
    
    # Regra específica: apenas códigos específicos são créditos
    if codigo_str in CODIGOS_CREDITO:
        return 'credito'
    else:
        return 'debito'

def categorizar_receita_por_codigo(codigo, descricao):
    """Categoriza receitas e descontos baseado no código e descrição"""
    codigo_str = str(codigo).strip()
    descricao = descricao.upper()
    
    # Classificar como crédito ou débito
    tipo_lancamento = classificar_lancamento_por_codigo(codigo_str)
    
    if tipo_lancamento == 'credito':
        # Categorização de créditos
        if 'SALARIO' in descricao or 'REMUNERACAO' in descricao:
            return 'Salário', tipo_lancamento
        elif 'FERIAS' in descricao:
            return 'Férias', tipo_lancamento
        elif 'ADICIONAL' in descricao or 'TEMPO' in descricao:
            return 'Adicional Tempo Serviço', tipo_lancamento
        elif 'INCORPORACAO' in descricao:
            return 'Incorporação', tipo_lancamento
        elif 'JUDICIAL' in descricao:
            return 'Decisão Judicial', tipo_lancamento
        else:
            return 'Outros Proventos', tipo_lancamento
    
    else:  # débito
        # Categorização de débitos
        if 'INSS' in descricao:
            return 'INSS', tipo_lancamento
        elif 'IMPOSTO' in descricao or 'RENDA' in descricao:
            return 'Imposto de Renda', tipo_lancamento
        elif 'FUNCEF' in descricao or 'PREVIDENCIA' in descricao:
            return 'Previdência Privada', tipo_lancamento
        elif 'SINDICATO' in descricao:
            return 'Sindicato', tipo_lancamento
        elif 'SAUDE' in descricao or 'MEDICO' in descricao:
            return 'Plano de Saúde', tipo_lancamento
        elif 'CONSIGNACOES' in descricao or 'EMPRESTIMO' in descricao:
            return 'Empréstimo Consignado', tipo_lancamento
        elif 'GYMPASS' in descricao or 'CONVENIO' in descricao:
            return 'Convênios', tipo_lancamento
        elif 'ASSOCIACAO' in descricao:
            return 'Associação', tipo_lancamento
        elif 'CREDITO' in descricao or 'DEVOLVER' in descricao:
            return 'Ajustes/Devoluções', tipo_lancamento
        elif 'REP' in descricao or 'REPOSICAO' in descricao:
            return 'Reposições', tipo_lancamento
        else:
            return 'Outros Descontos', tipo_lancamento

def processar_pdf_fatura(file_bytes, nome_arquivo):
    """Processa PDF de fatura com múltiplos padrões robustos"""
    texto = extrair_texto_pdf(file_bytes)
    
    if not texto.strip():
        st.error("❌ Não foi possível extrair texto do PDF")
        return []
    
    # Debug: mostrar texto extraído
    with st.expander("🔍 Debug - Texto Extraído"):
        debug_texto_extraido(texto)
    
    transacoes = []
    
    # Detectar cartão baseado no nome do arquivo e conteúdo
    cartao = detectar_cartao(nome_arquivo, texto)
    
    # Múltiplos padrões para diferentes formatos de fatura
    padroes_fatura = [
        # Padrão 1: DD/MM/YYYY ESTABELECIMENTO VALOR
        r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z0-9\s\-\.\*\&\+]+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 2: DD/MM ESTABELECIMENTO VALOR
        r'(\d{1,2}/\d{1,2})\s+([A-Za-z0-9\s\-\.\*\&\+]+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 3: Com separadores |
        r'(\d{1,2}/\d{1,2}/\d{4})\s*\|\s*([A-Za-z0-9\s\-\.\*\&\+]+?)\s*\|\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 4: DD-MM-YYYY
        r'(\d{1,2}-\d{1,2}-\d{4})\s+([A-Za-z0-9\s\-\.\*\&\+]+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 5: Com R$ explícito
        r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z0-9\s\-\.\*\&\+]+?)\s+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 6: Formato mais flexível
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*[|\s]\s*([A-Za-z0-9\s\-\.\*\&\+]{3,50}?)\s*[|\s]\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão 7: Azul específico
        r'(\d{2}/\d{2})\s+([A-Z\s\-\.\*]+)\s+(\d+,\d{2})\s+(\d+,\d{2})',
        
        # Padrão 8: Santander específico
        r'(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([A-Z\s\-\.\*]+)\s+(\d+,\d{2})',
        
        # Padrão 9: Samsung específico
        r'(\d{2}/\d{2})\s+([A-Z0-9\s\-\.\*]+)\s+(\d+,\d{2})',
        
        # Padrão 10: Genérico com tabs
        r'(\d{1,2}/\d{1,2}/\d{2,4})\t+([A-Za-z0-9\s\-\.\*\&\+]+?)\t+(\d{1,3}(?:\.\d{3})*,\d{2})'
    ]
    
    matches_encontrados = 0
    
    for i, padrao in enumerate(padroes_fatura):
        matches = re.findall(padrao, texto, re.MULTILINE | re.IGNORECASE)
        
        if matches:
            st.info(f"✅ Padrão {i+1} encontrou {len(matches)} transações")
            
            for match in matches:
                try:
                    if len(match) >= 3:
                        data_str = match[0]
                        estabelecimento = match[1].strip()
                        valor_str = match[-1]  # Último elemento é sempre o valor
                        
                        # Limpar estabelecimento
                        estabelecimento = re.sub(r'\s+', ' ', estabelecimento)
                        estabelecimento = estabelecimento[:50]  # Limitar tamanho
                        
                        # Converter data
                        data_obj = converter_data(data_str)
                        if not data_obj:
                            continue
                        
                        # Converter valor
                        valor = converter_valor(valor_str)
                        if valor <= 0:
                            continue
                        
                        # Filtrar estabelecimentos muito curtos
                        if len(estabelecimento.strip()) < 3:
                            continue
                        
                        categoria = categorizar_estabelecimento(estabelecimento)
                        
                        transacoes.append({
                            'data': data_obj,
                            'estabelecimento': estabelecimento,
                            'categoria': categoria,
                            'valor': valor,
                            'cartao': cartao,
                            'arquivo_origem': nome_arquivo
                        })
                        matches_encontrados += 1
                        
                except Exception as e:
                    continue
    
    # Se não encontrou nada, tentar extração alternativa
    if not transacoes:
        st.warning("⚠️ Padrões principais não funcionaram. Tentando extração alternativa...")
        transacoes = extrair_transacoes_alternativo(texto, cartao, nome_arquivo)
    
    # Remover duplicatas
    transacoes = remover_duplicatas_transacoes(transacoes)
    
    st.success(f"✅ Total de {len(transacoes)} transações extraídas")
    
    return transacoes

def extrair_transacoes_alternativo(texto, cartao, nome_arquivo):
    """Método alternativo de extração quando padrões principais falham"""
    transacoes = []
    
    # Procurar por valores monetários no texto
    valores = re.findall(r'R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})', texto)
    datas = re.findall(r'(\d{1,2}[/\-]\d{1,2}[/\-]?\d{0,4})', texto)
    
    if valores and datas:
        st.info(f"🔍 Método alternativo encontrou {len(valores)} valores e {len(datas)} datas")
        
        # Tentar combinar datas e valores próximos
        linhas = texto.split('\n')
        for linha in linhas:
            if re.search(r'\d{1,2}[/\-]\d{1,2}', linha) and re.search(r'\d+,\d{2}', linha):
                # Esta linha tem data e valor
                try:
                    data_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]?\d{0,4})', linha)
                    valor_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', linha)
                    
                    if data_match and valor_match:
                        data_obj = converter_data(data_match.group(1))
                        valor = converter_valor(valor_match.group(1))
                        
                        if data_obj and valor > 0:
                            # Extrair estabelecimento (texto entre data e valor)
                            estabelecimento = linha.replace(data_match.group(1), '').replace(valor_match.group(1), '')
                            estabelecimento = re.sub(r'[R\$\|\t]+', ' ', estabelecimento).strip()
                            
                            if len(estabelecimento) >= 3:
                                categoria = categorizar_estabelecimento(estabelecimento)
                                
                                transacoes.append({
                                    'data': data_obj,
                                    'estabelecimento': estabelecimento[:50],
                                    'categoria': categoria,
                                    'valor': valor,
                                    'cartao': cartao,
                                    'arquivo_origem': nome_arquivo
                                })
                except Exception:
                    continue
    
    return transacoes

def remover_duplicatas_transacoes(transacoes):
    """Remove transações duplicadas"""
    if not transacoes:
        return []
    
    # Criar chave única para cada transação
    transacoes_unicas = {}
    
    for transacao in transacoes:
        chave = f"{transacao['data']}_{transacao['estabelecimento']}_{transacao['valor']}"
        if chave not in transacoes_unicas:
            transacoes_unicas[chave] = transacao
    
    return list(transacoes_unicas.values())

def processar_pdf_contracheque(file_bytes, nome_arquivo):
    """Processa PDF de contracheque com regras específicas de classificação e correção de ano"""
    texto = extrair_texto_pdf(file_bytes)
    
    if not texto.strip():
        st.error("❌ Não foi possível extrair texto do PDF")
        return [], []
    
    # Debug: mostrar texto extraído
    with st.expander("🔍 Debug - Texto Extraído do Contracheque"):
        debug_texto_extraido(texto)
    
    receitas = []
    descontos = []
    
    # Detectar empresa/fonte
    fonte = detectar_fonte_contracheque(nome_arquivo, texto)
    
    # Padrões específicos para o formato do contracheque
    padroes_contracheque = [
        # Padrão principal: CODIGO DESCRICAO MM/YYYY [OUTROS] R$ VALOR
        r'(\d{2,5})\s+([A-Z\s\-\.\(\)/]+?)\s+(\d{2}/\d{4})\s+(?:\d{3}\s+)?R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão alternativo: CODIGO DESCRICAO MM/YYYY VALOR (sem R$)
        r'(\d{2,5})\s+([A-Z\s\-\.\(\)/]+?)\s+(\d{2}/\d{4})\s+(?:\d{3}\s+)?(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão sem data: CODIGO DESCRICAO R$ VALOR
        r'(\d{2,5})\s+([A-Z\s\-\.\(\)/]+?)\s+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        
        # Padrão flexível: qualquer linha com código e valor
        r'^(\d{2,5})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})$'
    ]
    
    matches_encontrados = 0
    data_referencia = extrair_data_contracheque(texto)
    
    st.info(f"📅 Data de referência detectada: {data_referencia}")
    
    for i, padrao in enumerate(padroes_contracheque):
        matches = re.findall(padrao, texto, re.MULTILINE)
        
        if matches:
            st.info(f"✅ Padrão contracheque {i+1} encontrou {len(matches)} itens")
            
            for match in matches:
                try:
                    if len(match) == 4:  # Padrão com data
                        codigo = match[0]
                        descricao = match[1].strip()
                        data_str = match[2]
                        valor_str = match[3]
                        
                        # Converter data específica com correção de ano
                        try:
                            mes, ano = data_str.split('/')
                            ano_int = int(ano)
                            
                            # Corrigir ano se necessário
                            if ano_int < 100:  # Ano de 2 dígitos
                                if ano_int < 50:  # 00-49 = 2000-2049
                                    ano_int += 2000
                                else:  # 50-99 = 1950-1999
                                    ano_int += 1900
                            
                            # Verificar se o ano é razoável
                            ano_atual = datetime.now().year
                            if ano_int < 2020 or ano_int > ano_atual + 2:
                                data_item = data_referencia
                            else:
                                data_item = datetime(ano_int, int(mes), 1).date()
                        except:
                            data_item = data_referencia
                    
                    elif len(match) == 3:  # Padrão sem data
                        codigo = match[0]
                        descricao = match[1].strip()
                        valor_str = match[2]
                        data_item = data_referencia
                    
                    else:
                        continue
                    
                    # Filtrar descrições muito curtas
                    if len(descricao) < 3:
                        continue
                    
                    # Converter valor
                    valor = converter_valor(valor_str)
                    if valor <= 0:
                        continue
                    
                    # Categorizar baseado no código e descrição
                    categoria, tipo_lancamento = categorizar_receita_por_codigo(codigo, descricao)
                    
                    if tipo_lancamento == 'credito':
                        # Adicionar como receita
                        receitas.append({
                            'data': data_item,
                            'descricao': descricao,
                            'categoria': categoria,
                            'valor': valor,
                            'fonte': fonte,
                            'codigo': codigo,
                            'tipo_lancamento': tipo_lancamento,
                            'arquivo_origem': nome_arquivo
                        })
                    else:
                        # Adicionar como desconto (despesa)
                        descontos.append({
                            'data': data_item,
                            'estabelecimento': f"Desconto: {descricao}",
                            'categoria': 'Descontos Folha',
                            'valor': valor,
                            'cartao': 'Contracheque',
                            'arquivo_origem': nome_arquivo
                        })
                        
                        # Também adicionar na tabela de receitas como débito para controle
                        receitas.append({
                            'data': data_item,
                            'descricao': descricao,
                            'categoria': categoria,
                            'valor': valor,
                            'fonte': fonte,
                            'codigo': codigo,
                            'tipo_lancamento': tipo_lancamento,
                            'arquivo_origem': nome_arquivo
                        })
                    
                    matches_encontrados += 1
                    
                except Exception as e:
                    st.warning(f"Erro ao processar item: {e}")
                    continue
    
    # Se não encontrou nada, tentar extração alternativa
    if not receitas and not descontos:
        st.warning("⚠️ Padrões principais não funcionaram. Tentando extração alternativa...")
        receitas_alt, descontos_alt = extrair_contracheque_alternativo(texto, fonte, nome_arquivo, data_referencia)
        receitas.extend(receitas_alt)
        descontos.extend(descontos_alt)
    
    # Remover duplicatas
    receitas = remover_duplicatas_receitas(receitas)
    descontos = remover_duplicatas_transacoes(descontos)
    
    # Calcular totais para validação
    total_creditos = sum(r['valor'] for r in receitas if r.get('tipo_lancamento') == 'credito')
    total_debitos = sum(r['valor'] for r in receitas if r.get('tipo_lancamento') == 'debito')
    salario_liquido = total_creditos - total_debitos
    
    st.success(f"✅ Extraídas {len([r for r in receitas if r.get('tipo_lancamento') == 'credito'])} receitas e {len([r for r in receitas if r.get('tipo_lancamento') == 'debito'])} descontos")
    st.info(f"💰 Total Créditos: R$ {total_creditos:,.2f} | Total Débitos: R$ {total_debitos:,.2f} | Líquido: R$ {salario_liquido:,.2f}")
    
    return receitas, descontos

def detectar_fonte_contracheque(nome_arquivo, texto):
    """Detecta a fonte/empresa do contracheque"""
    nome_lower = nome_arquivo.lower()
    texto_lower = texto.lower()
    
    # Procurar por nomes de empresas conhecidas
    if 'caixa' in nome_lower or 'caixa' in texto_lower:
        return 'Caixa Econômica Federal'
    elif 'petrobras' in nome_lower or 'petrobras' in texto_lower:
        return 'Petrobras'
    elif 'vale' in nome_lower or 'vale' in texto_lower:
        return 'Vale'
    elif 'itau' in nome_lower or 'itau' in texto_lower:
        return 'Itaú'
    elif 'bradesco' in nome_lower or 'bradesco' in texto_lower:
        return 'Bradesco'
    elif 'banco do brasil' in nome_lower or 'banco do brasil' in texto_lower:
        return 'Banco do Brasil'
    
    return 'Empresa'

def extrair_data_contracheque(texto):
    """Extrai data de referência do contracheque com correção de ano"""
    # Procurar por padrões de data de referência
    padroes_data = [
        r'(\d{2}/\d{4})',  # MM/YYYY
        r'(\d{2}-\d{4})',  # MM-YYYY
        r'(JANEIRO|FEVEREIRO|MARÇO|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)\s*/?\s*(\d{4})',
        r'(\d{1,2})/(\d{4})'  # M/YYYY
    ]
    
    meses = {
        'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4,
        'MAIO': 5, 'JUNHO': 6, 'JULHO': 7, 'AGOSTO': 8,
        'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
    }
    
    for padrao in padroes_data:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        if matches:
            try:
                # Pegar a data mais comum (moda)
                if isinstance(matches[0], tuple):
                    if len(matches[0]) == 2:  # Mês por extenso + ano
                        mes_nome = matches[0][0].upper()
                        ano = int(matches[0][1])
                        if mes_nome in meses:
                            return datetime(ano, meses[mes_nome], 1).date()
                else:
                    # Formato MM/YYYY - pegar o mais frequente
                    datas_encontradas = {}
                    for match in matches:
                        if '/' in match or '-' in match:
                            partes = re.split('[/-]', match)
                            if len(partes) == 2:
                                mes = int(partes[0])
                                ano = int(partes[1])
                                
                                # Corrigir ano se necessário
                                if ano < 100:  # Ano de 2 dígitos
                                    if ano < 50:  # 00-49 = 2000-2049
                                        ano += 2000
                                    else:  # 50-99 = 1950-1999
                                        ano += 1900
                                
                                # Verificar se o ano é razoável
                                ano_atual = datetime.now().year
                                if 2020 <= ano <= ano_atual + 2 and 1 <= mes <= 12:
                                    data_key = f"{mes:02d}/{ano}"
                                    datas_encontradas[data_key] = datas_encontradas.get(data_key, 0) + 1
                    
                    if datas_encontradas:
                        # Pegar a data mais frequente
                        data_mais_comum = max(datas_encontradas, key=datas_encontradas.get)
                        mes, ano = data_mais_comum.split('/')
                        return datetime(int(ano), int(mes), 1).date()
            except:
                continue
    
    # Se não encontrou, usar data atual
    return datetime.now().date()

def extrair_contracheque_alternativo(texto, fonte, nome_arquivo, data_referencia):
    """Método alternativo para extrair dados de contracheque"""
    receitas = []
    descontos = []
    
    # Procurar por valores monetários e tentar associar com descrições
    linhas = texto.split('\n')
    
    for linha in linhas:
        # Procurar por linhas que tenham código numérico e valor
        if re.search(r'^\d{2,5}\s+', linha) and re.search(r'\d+,\d{2}', linha):
            try:
                # Extrair código
                codigo_match = re.search(r'^(\d{2,5})', linha)
                if not codigo_match:
                    continue
                
                codigo = codigo_match.group(1)
                
                # Extrair valor
                valor_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', linha)
                if not valor_match:
                    continue
                
                valor = converter_valor(valor_match.group(1))
                if valor <= 10:  # Filtrar valores muito baixos
                    continue
                
                # Extrair descrição (texto entre código e valor)
                descricao = linha.replace(codigo_match.group(1), '').replace(valor_match.group(1), '')
                descricao = re.sub(r'[R\$\|\t\d/]+', ' ', descricao).strip()
                
                if len(descricao) >= 3:
                    categoria, tipo_lancamento = categorizar_receita_por_codigo(codigo, descricao)
                    
                    if tipo_lancamento == 'credito':
                        receitas.append({
                            'data': data_referencia,
                            'descricao': descricao,
                            'categoria': categoria,
                            'valor': valor,
                            'fonte': fonte,
                            'codigo': codigo,
                            'tipo_lancamento': tipo_lancamento,
                            'arquivo_origem': nome_arquivo
                        })
                    else:
                        descontos.append({
                            'data': data_referencia,
                            'estabelecimento': f"Desconto: {descricao}",
                            'categoria': 'Descontos Folha',
                            'valor': valor,
                            'cartao': 'Contracheque',
                            'arquivo_origem': nome_arquivo
                        })
                        
                        # Também adicionar na tabela de receitas como débito
                        receitas.append({
                            'data': data_referencia,
                            'descricao': descricao,
                            'categoria': categoria,
                            'valor': valor,
                            'fonte': fonte,
                            'codigo': codigo,
                            'tipo_lancamento': tipo_lancamento,
                            'arquivo_origem': nome_arquivo
                        })
            except Exception:
                continue
    
    return receitas, descontos

def remover_duplicatas_receitas(receitas):
    """Remove receitas duplicadas"""
    if not receitas:
        return []
    
    receitas_unicas = {}
    
    for receita in receitas:
        chave = f"{receita['data']}_{receita['descricao']}_{receita['valor']}_{receita.get('codigo', '')}"
        if chave not in receitas_unicas:
            receitas_unicas[chave] = receita
    
    return list(receitas_unicas.values())

@st.cache_data
def carregar_dados():
    """Carrega dados do banco"""
    # Inicializar banco se não existir
    if not os.path.exists(DB_PATH):
        init_database()
    
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    try:
        # Carregar transações (despesas)
        df_transacoes = pd.read_sql_query(
            "SELECT * FROM transacoes ORDER BY data DESC", 
            conn
        )
        
        # Carregar receitas
        df_receitas = pd.read_sql_query(
            "SELECT * FROM receitas ORDER BY data DESC", 
            conn
        )
        
        # Carregar arquivos processados
        df_arquivos = pd.read_sql_query(
            "SELECT * FROM arquivos_processados ORDER BY data_processamento DESC", 
            conn
        )
        
        # Converter colunas de data
        if not df_transacoes.empty:
            df_transacoes['data'] = pd.to_datetime(df_transacoes['data']).dt.date
        
        if not df_receitas.empty:
            df_receitas['data'] = pd.to_datetime(df_receitas['data']).dt.date
        
        return df_transacoes, df_receitas, df_arquivos
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        conn.close()

def salvar_transacoes(transacoes, nome_arquivo, hash_arquivo):
    """Salva transações no banco de dados"""
    if not transacoes:
        return 0
    
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        transacoes_salvas = 0
        
        for transacao in transacoes:
            try:
                cursor.execute('''
                    INSERT INTO transacoes (data, estabelecimento, categoria, valor, cartao, arquivo_origem)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transacao['data'],
                    transacao['estabelecimento'],
                    transacao['categoria'],
                    transacao['valor'],
                    transacao['cartao'],
                    transacao['arquivo_origem']
                ))
                transacoes_salvas += 1
            except Exception as e:
                st.error(f"Erro ao salvar transação: {e}")
                continue
        
        # Registrar arquivo processado
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO arquivos_processados 
                (nome_arquivo, hash_arquivo, tipo_arquivo, total_transacoes)
                VALUES (?, ?, ?, ?)
            ''', (nome_arquivo, hash_arquivo, 'fatura', transacoes_salvas))
        except Exception as e:
            st.error(f"Erro ao registrar arquivo: {e}")
        
        conn.commit()
        return transacoes_salvas
        
    except Exception as e:
        st.error(f"Erro ao salvar transações: {e}")
        return 0
    finally:
        conn.close()

def salvar_receitas(receitas, nome_arquivo, hash_arquivo):
    """Salva receitas no banco de dados"""
    if not receitas:
        return 0
    
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        receitas_salvas = 0
        
        for receita in receitas:
            try:
                cursor.execute('''
                    INSERT INTO receitas (data, descricao, categoria, valor, fonte, codigo, tipo_lancamento, arquivo_origem)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    receita['data'],
                    receita['descricao'],
                    receita['categoria'],
                    receita['valor'],
                    receita['fonte'],
                    receita.get('codigo', ''),
                    receita.get('tipo_lancamento', 'credito'),
                    receita['arquivo_origem']
                ))
                receitas_salvas += 1
            except Exception as e:
                st.error(f"Erro ao salvar receita: {e}")
                continue
        
        # Registrar arquivo processado
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO arquivos_processados 
                (nome_arquivo, hash_arquivo, tipo_arquivo, total_transacoes)
                VALUES (?, ?, ?, ?)
            ''', (nome_arquivo, hash_arquivo, 'contracheque', receitas_salvas))
        except Exception as e:
            st.error(f"Erro ao registrar arquivo: {e}")
        
        conn.commit()
        return receitas_salvas
        
    except Exception as e:
        st.error(f"Erro ao salvar receitas: {e}")
        return 0
    finally:
        conn.close()

def limpar_cache():
    """Limpa o cache do Streamlit"""
    st.cache_data.clear()

def verificar_arquivo_processado(file_hash):
    """Verifica se arquivo já foi processado"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nome_arquivo FROM arquivos_processados WHERE hash_arquivo = ?",
            (file_hash,)
        )
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Exception as e:
        st.error(f"Erro ao verificar arquivo: {e}")
        return None
    finally:
        conn.close()

def obter_meses_disponiveis(df_receitas):
    """Obtém lista de meses disponíveis nos dados"""
    if df_receitas.empty:
        return []
    
    df_receitas['mes_ano'] = pd.to_datetime(df_receitas['data']).dt.strftime('%Y-%m')
    meses = sorted(df_receitas['mes_ano'].unique(), reverse=True)
    return meses

def filtrar_dados_por_mes(df_receitas, mes_selecionado):
    """Filtra dados por mês específico"""
    if df_receitas.empty or not mes_selecionado:
        return df_receitas
    
    df_receitas['mes_ano'] = pd.to_datetime(df_receitas['data']).dt.strftime('%Y-%m')
    return df_receitas[df_receitas['mes_ano'] == mes_selecionado]

def calcular_acumulado_anual(df_receitas):
    """Calcula totais acumulados por rubrica/código no ano"""
    if df_receitas.empty:
        return pd.DataFrame()
    
    # Filtrar apenas dados do ano atual
    ano_atual = datetime.now().year
    df_ano = df_receitas[pd.to_datetime(df_receitas['data']).dt.year == ano_atual]
    
    if df_ano.empty:
        return pd.DataFrame()
    
    # Agrupar por código e categoria
    acumulado = df_ano.groupby(['codigo', 'categoria', 'tipo_lancamento']).agg({
        'valor': 'sum',
        'descricao': 'first'
    }).reset_index()
    
    # Ordenar por valor decrescente
    acumulado = acumulado.sort_values('valor', ascending=False)
    
    return acumulado

def verificar_colunas_existem(df, colunas_necessarias):
    """Verifica se as colunas necessárias existem no DataFrame"""
    if df.empty:
        return []
    
    colunas_existentes = []
    for coluna in colunas_necessarias:
        if coluna in df.columns:
            colunas_existentes.append(coluna)
    
    return colunas_existentes

# Interface principal
def main():
    st.title("💰 Dashboard Financeiro Automatizado")
    st.markdown("Sistema inteligente de análise financeira com upload automático de faturas")
    
    # Inicializar banco de dados
    if not os.path.exists(DB_PATH):
        with st.spinner("🔄 Inicializando banco de dados..."):
            init_database()
    
    # Carregar dados
    df_transacoes, df_receitas, df_arquivos = carregar_dados()
    
    # Sidebar para navegação
    st.sidebar.title("📊 Navegação")
    opcao = st.sidebar.selectbox(
        "Escolha uma seção:",
        [
            "📤 Upload de Faturas",
            "💰 Upload de Receitas", 
            "📈 Dashboard",
            "📊 Resultado Financeiro",
            "📅 Análise Mensal",
            "📈 Visão Anual",
            "📋 Transações",
            "💵 Receitas",
            "📁 Arquivos",
            "⚙️ Configurações"
        ]
    )
    
    if opcao == "📤 Upload de Faturas":
        st.header("📤 Upload de Faturas")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📄 Faça upload de suas faturas em PDF")
            st.markdown("Suporte para cartões: Azul, Santander, Caixa Elo, Caixa Visa, Samsung")
            
            uploaded_file = st.file_uploader(
                "Escolha um arquivo PDF",
                type="pdf",
                help="Selecione a fatura do seu cartão de crédito em formato PDF"
            )
            
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                file_hash = calcular_hash_arquivo(file_bytes)
                
                # Verificar se arquivo já foi processado
                arquivo_existente = verificar_arquivo_processado(file_hash)
                
                if arquivo_existente:
                    st.error(f"❌ Arquivo já foi processado anteriormente: {arquivo_existente}")
                else:
                    # Processar arquivo
                    with st.spinner("🔄 Processando fatura..."):
                        transacoes = processar_pdf_fatura(file_bytes, uploaded_file.name)
                    
                    if transacoes:
                        transacoes_salvas = salvar_transacoes(transacoes, uploaded_file.name, file_hash)
                        limpar_cache()  # Limpar cache para atualizar dados
                        
                        st.success(f"✅ Fatura processada com sucesso! {transacoes_salvas} transações adicionadas.")
                        
                        # Mostrar preview das transações
                        st.subheader("💳 Preview das Transações")
                        df_preview = pd.DataFrame(transacoes)
                        df_preview['valor'] = df_preview['valor'].apply(lambda x: f"R$ {x:,.2f}")
                        st.dataframe(df_preview, use_container_width=True)
                    else:
                        st.error("❌ Não foi possível extrair transações do arquivo. Verifique se é uma fatura válida.")
        
        with col2:
            st.markdown("### 💡 Como funciona:")
            st.markdown("""
            1. **📤 Upload**: Envie sua fatura em PDF
            2. **🔍 Extração**: Sistema extrai transações automaticamente
            3. **🏷️ Categorização**: Gastos são categorizados inteligentemente
            4. **🔄 Detecção**: Evita duplicatas automaticamente
            5. **📊 Atualização**: Dashboard é atualizado em tempo real
            """)
            
            st.markdown("### 📊 Estatísticas")
            if not df_transacoes.empty:
                st.metric("Total de Transações", len(df_transacoes))
                st.metric("Faturas Processadas", len(df_arquivos[df_arquivos['tipo_arquivo'] == 'fatura']) if 'tipo_arquivo' in df_arquivos.columns else 0)
                st.metric("Total Gasto", f"R$ {df_transacoes['valor'].sum():,.2f}")
            else:
                st.info("📤 Faça upload de faturas para ver estatísticas")
    
    elif opcao == "💰 Upload de Receitas":
        st.header("💰 Upload de Receitas")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 💵 Faça upload de seus contracheques em PDF")
            st.markdown("Sistema extrai automaticamente salários, bonificações e benefícios")
            
            # Mostrar regras de classificação
            with st.expander("📋 Regras de Classificação"):
                st.markdown(f"""
                **Códigos de Crédito (Receitas):**
                {', '.join(CODIGOS_CREDITO)}
                
                **Códigos de Débito:**
                Todos os demais códigos (21201, 31143, 4313, 4325, etc.)
                """)
            
            uploaded_file = st.file_uploader(
                "Escolha um contracheque PDF",
                type="pdf",
                help="Selecione seu contracheque em formato PDF"
            )
            
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                file_hash = calcular_hash_arquivo(file_bytes)
                
                # Verificar se arquivo já foi processado
                arquivo_existente = verificar_arquivo_processado(file_hash)
                
                if arquivo_existente:
                    st.error(f"❌ Arquivo já foi processado anteriormente: {arquivo_existente}")
                else:
                    # Processar arquivo
                    with st.spinner("🔄 Processando contracheque..."):
                        receitas, descontos = processar_pdf_contracheque(file_bytes, uploaded_file.name)
                    
                    total_processados = 0
                    
                    if receitas:
                        receitas_salvas = salvar_receitas(receitas, uploaded_file.name, file_hash)
                        total_processados += receitas_salvas
                    
                    if descontos:
                        descontos_salvos = salvar_transacoes(descontos, uploaded_file.name, file_hash)
                        total_processados += descontos_salvos
                    
                    if total_processados > 0:
                        limpar_cache()  # Limpar cache para atualizar dados
                        
                        st.success(f"✅ Contracheque processado com sucesso! {total_processados} lançamentos adicionados.")
                        
                        # Mostrar preview das receitas
                        if receitas:
                            st.subheader("💵 Preview dos Lançamentos")
                            df_preview_receitas = pd.DataFrame(receitas)
                            df_preview_receitas['valor'] = df_preview_receitas['valor'].apply(lambda x: f"R$ {x:,.2f}")
                            
                            # Verificar colunas existentes
                            colunas_preview = verificar_colunas_existem(df_preview_receitas, ['codigo', 'descricao', 'categoria', 'tipo_lancamento', 'valor'])
                            if colunas_preview:
                                st.dataframe(df_preview_receitas[colunas_preview], use_container_width=True)
                            else:
                                st.dataframe(df_preview_receitas, use_container_width=True)
                    else:
                        st.error("❌ Não foi possível extrair dados do arquivo. Verifique se é um contracheque válido.")
        
        with col2:
            st.markdown("### 💡 Como funciona:")
            st.markdown("""
            1. **📤 Upload**: Envie seu contracheque em PDF
            2. **🔍 Extração**: Sistema extrai receitas automaticamente
            3. **🏷️ Categorização**: Receitas são categorizadas por código
            4. **🔄 Classificação**: Créditos vs Débitos conforme regras
            5. **📊 Atualização**: Dashboard é atualizado em tempo real
            """)
            
            st.markdown("### 📊 Estatísticas de Receitas")
            if not df_receitas.empty:
                total_creditos = df_receitas[df_receitas.get('tipo_lancamento', 'credito') == 'credito']['valor'].sum() if 'tipo_lancamento' in df_receitas.columns else df_receitas['valor'].sum()
                total_debitos = df_receitas[df_receitas.get('tipo_lancamento', 'credito') == 'debito']['valor'].sum() if 'tipo_lancamento' in df_receitas.columns else 0
                
                st.metric("Total Créditos", f"R$ {total_creditos:,.2f}")
                st.metric("Total Débitos", f"R$ {total_debitos:,.2f}")
                st.metric("Líquido", f"R$ {total_creditos - total_debitos:,.2f}")
            else:
                st.info("📤 Faça upload de contracheques para ver estatísticas")
    
    elif opcao == "📅 Análise Mensal":
        st.header("📅 Análise Mensal")
        
        if df_receitas.empty:
            st.info("📤 Nenhum contracheque encontrado. Faça upload de seus contracheques para ver a análise mensal.")
            return
        
        # Filtro por mês
        meses_disponiveis = obter_meses_disponiveis(df_receitas)
        
        if not meses_disponiveis:
            st.info("📅 Nenhum mês disponível para análise.")
            return
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            mes_selecionado = st.selectbox(
                "Selecione o mês:",
                options=['Todos os meses'] + meses_disponiveis,
                index=1 if len(meses_disponiveis) > 0 else 0
            )
        
        # Filtrar dados
        if mes_selecionado != 'Todos os meses':
            df_mes = filtrar_dados_por_mes(df_receitas, mes_selecionado)
            st.subheader(f"📊 Análise de {mes_selecionado}")
        else:
            df_mes = df_receitas
            st.subheader("📊 Análise Geral")
        
        if df_mes.empty:
            st.info("📅 Nenhum dado encontrado para o período selecionado.")
            return
        
        # Separar créditos e débitos
        df_creditos = df_mes[df_mes.get('tipo_lancamento', 'credito') == 'credito'] if 'tipo_lancamento' in df_mes.columns else df_mes
        df_debitos = df_mes[df_mes.get('tipo_lancamento', 'credito') == 'debito'] if 'tipo_lancamento' in df_mes.columns else pd.DataFrame()
        
        # Métricas do mês
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_creditos = df_creditos['valor'].sum()
            st.metric("💰 Total Créditos", f"R$ {total_creditos:,.2f}")
        
        with col2:
            total_debitos = df_debitos['valor'].sum() if not df_debitos.empty else 0
            st.metric("💸 Total Débitos", f"R$ {total_debitos:,.2f}")
        
        with col3:
            liquido = total_creditos - total_debitos
            st.metric("📈 Líquido", f"R$ {liquido:,.2f}")
        
        # Tabelas detalhadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Créditos")
            if not df_creditos.empty:
                df_creditos_display = df_creditos.copy()
                df_creditos_display['valor'] = df_creditos_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Verificar colunas existentes
                colunas_creditos = verificar_colunas_existem(df_creditos_display, ['codigo', 'descricao', 'categoria', 'valor'])
                if colunas_creditos:
                    st.dataframe(
                        df_creditos_display[colunas_creditos],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_creditos_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum crédito encontrado")
        
        with col2:
            st.subheader("💸 Débitos")
            if not df_debitos.empty:
                df_debitos_display = df_debitos.copy()
                df_debitos_display['valor'] = df_debitos_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Verificar colunas existentes
                colunas_debitos = verificar_colunas_existem(df_debitos_display, ['codigo', 'descricao', 'categoria', 'valor'])
                if colunas_debitos:
                    st.dataframe(
                        df_debitos_display[colunas_debitos],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_debitos_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum débito encontrado")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_creditos.empty:
                st.subheader("🥧 Créditos por Categoria")
                creditos_categoria = df_creditos.groupby('categoria')['valor'].sum().reset_index()
                fig_creditos = px.pie(
                    creditos_categoria,
                    values='valor',
                    names='categoria',
                    title="Distribuição de Créditos"
                )
                st.plotly_chart(fig_creditos, use_container_width=True)
        
        with col2:
            if not df_debitos.empty:
                st.subheader("🥧 Débitos por Categoria")
                debitos_categoria = df_debitos.groupby('categoria')['valor'].sum().reset_index()
                fig_debitos = px.pie(
                    debitos_categoria,
                    values='valor',
                    names='categoria',
                    title="Distribuição de Débitos"
                )
                st.plotly_chart(fig_debitos, use_container_width=True)
    
    elif opcao == "📈 Visão Anual":
        st.header("📈 Visão Anual Acumulada")
        
        if df_receitas.empty:
            st.info("📤 Nenhum contracheque encontrado. Faça upload de seus contracheques para ver a visão anual.")
            return
        
        # Calcular acumulado anual
        df_acumulado = calcular_acumulado_anual(df_receitas)
        
        if df_acumulado.empty:
            st.info("📅 Nenhum dado encontrado para o ano atual.")
            return
        
        ano_atual = datetime.now().year
        st.subheader(f"📊 Totais Acumulados - {ano_atual}")
        
        # Separar créditos e débitos
        df_creditos_acum = df_acumulado[df_acumulado['tipo_lancamento'] == 'credito']
        df_debitos_acum = df_acumulado[df_acumulado['tipo_lancamento'] == 'debito']
        
        # Métricas anuais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_creditos_ano = df_creditos_acum['valor'].sum()
            st.metric("💰 Total Créditos (Ano)", f"R$ {total_creditos_ano:,.2f}")
        
        with col2:
            total_debitos_ano = df_debitos_acum['valor'].sum()
            st.metric("💸 Total Débitos (Ano)", f"R$ {total_debitos_ano:,.2f}")
        
        with col3:
            liquido_ano = total_creditos_ano - total_debitos_ano
            st.metric("📈 Líquido (Ano)", f"R$ {liquido_ano:,.2f}")
        
        # Tabelas de acumulado
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Créditos Acumulados por Rubrica")
            if not df_creditos_acum.empty:
                df_creditos_display = df_creditos_acum.copy()
                df_creditos_display['valor'] = df_creditos_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Verificar colunas existentes
                colunas_creditos_acum = verificar_colunas_existem(df_creditos_display, ['codigo', 'categoria', 'valor'])
                if colunas_creditos_acum:
                    st.dataframe(
                        df_creditos_display[colunas_creditos_acum],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_creditos_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum crédito acumulado")
        
        with col2:
            st.subheader("💸 Débitos Acumulados por Rubrica")
            if not df_debitos_acum.empty:
                df_debitos_display = df_debitos_acum.copy()
                df_debitos_display['valor'] = df_debitos_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                
                # Verificar colunas existentes
                colunas_debitos_acum = verificar_colunas_existem(df_debitos_display, ['codigo', 'categoria', 'valor'])
                if colunas_debitos_acum:
                    st.dataframe(
                        df_debitos_display[colunas_debitos_acum],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.dataframe(df_debitos_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum débito acumulado")
        
        # Gráficos de barras
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_creditos_acum.empty:
                st.subheader("📊 Top 10 Créditos")
                top_creditos = df_creditos_acum.head(10)
                fig_creditos_bar = px.bar(
                    top_creditos,
                    x='valor',
                    y='categoria',
                    orientation='h',
                    title="Maiores Créditos Acumulados",
                    text='valor'
                )
                fig_creditos_bar.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_creditos_bar, use_container_width=True)
        
        with col2:
            if not df_debitos_acum.empty:
                st.subheader("📊 Top 10 Débitos")
                top_debitos = df_debitos_acum.head(10)
                fig_debitos_bar = px.bar(
                    top_debitos,
                    x='valor',
                    y='categoria',
                    orientation='h',
                    title="Maiores Débitos Acumulados",
                    text='valor',
                    color_discrete_sequence=['red']
                )
                fig_debitos_bar.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_debitos_bar, use_container_width=True)
    
    elif opcao == "📈 Dashboard":
        st.header("📈 Dashboard Financeiro")
        
        if df_transacoes.empty:
            st.info("📤 Nenhuma transação encontrada. Faça upload de suas faturas para ver o dashboard.")
            return
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_gastos = df_transacoes['valor'].sum()
            st.metric("💰 Total de Gastos", f"R$ {total_gastos:,.2f}")
        
        with col2:
            total_transacoes = len(df_transacoes)
            st.metric("📊 Total de Transações", total_transacoes)
        
        with col3:
            valor_medio = df_transacoes['valor'].mean()
            st.metric("📈 Valor Médio", f"R$ {valor_medio:,.2f}")
        
        with col4:
            categoria_principal = df_transacoes.groupby('categoria')['valor'].sum().idxmax()
            st.metric("🏆 Categoria Principal", categoria_principal)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza por categoria
            st.subheader("🥧 Gastos por Categoria")
            gastos_categoria = df_transacoes.groupby('categoria')['valor'].sum().reset_index()
            fig_pizza = px.pie(
                gastos_categoria,
                values='valor',
                names='categoria',
                title="Distribuição de Gastos por Categoria"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col2:
            # Gráfico de barras por cartão
            st.subheader("💳 Gastos por Cartão")
            gastos_cartao = df_transacoes.groupby('cartao')['valor'].sum().reset_index()
            fig_barras = px.bar(
                gastos_cartao,
                x='cartao',
                y='valor',
                title="Gastos por Cartão de Crédito"
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        
        # Análise temporal
        st.subheader("📅 Análise Temporal")
        
        # Adicionar coluna de mês/ano
        df_transacoes['mes_ano'] = pd.to_datetime(df_transacoes['data']).dt.to_period('M')
        df_transacoes['mes'] = pd.to_datetime(df_transacoes['data']).dt.strftime('%Y-%m')
        
        # Evolução mensal
        evolucao_mensal = df_transacoes.groupby('mes')['valor'].sum().reset_index()
        fig_evolucao = px.line(
            evolucao_mensal,
            x='mes',
            y='valor',
            title="Evolução dos Gastos Mensais",
            markers=True
        )
        fig_evolucao.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)")
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Heatmap categoria x mês
        st.subheader("🔥 Heatmap: Gastos por Categoria e Mês")
        heatmap_data = df_transacoes.pivot_table(
            values='valor',
            index='categoria',
            columns='mes',
            aggfunc='sum',
            fill_value=0
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Gastos por Categoria e Mês",
            color_continuous_scale='RdYlBu_r',
            aspect='auto'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    elif opcao == "📊 Resultado Financeiro":
        st.header("📊 Resultado Financeiro")
        
        # Calcular totais
        total_receitas = df_receitas[df_receitas.get('tipo_lancamento', 'credito') == 'credito']['valor'].sum() if not df_receitas.empty and 'tipo_lancamento' in df_receitas.columns else (df_receitas['valor'].sum() if not df_receitas.empty else 0)
        total_despesas = df_transacoes['valor'].sum() if not df_transacoes.empty else 0
        total_descontos = df_receitas[df_receitas.get('tipo_lancamento', 'credito') == 'debito']['valor'].sum() if not df_receitas.empty and 'tipo_lancamento' in df_receitas.columns else 0
        
        resultado_liquido = total_receitas - total_despesas - total_descontos
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total de Receitas", f"R$ {total_receitas:,.2f}")
        
        with col2:
            st.metric("💸 Total de Despesas", f"R$ {total_despesas:,.2f}")
        
        with col3:
            st.metric("📉 Descontos Folha", f"R$ {total_descontos:,.2f}")
        
        with col4:
            cor_resultado = "normal" if resultado_liquido >= 0 else "inverse"
            st.metric(
                "📈 Resultado Líquido", 
                f"R$ {resultado_liquido:,.2f}",
                delta=f"{'Superávit' if resultado_liquido >= 0 else 'Déficit'}"
            )
        
        # Gráfico de resultado
        if total_receitas > 0 or total_despesas > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras comparativo
                st.subheader("📊 Receitas vs Despesas")
                dados_comparativo = pd.DataFrame({
                    'Tipo': ['Receitas', 'Despesas Cartão', 'Descontos Folha'],
                    'Valor': [total_receitas, total_despesas, total_descontos]
                })
                
                fig_comparativo = px.bar(
                    dados_comparativo,
                    x='Tipo',
                    y='Valor',
                    title="Comparativo Receitas vs Despesas",
                    color='Tipo',
                    color_discrete_map={'Receitas': 'green', 'Despesas Cartão': 'red', 'Descontos Folha': 'orange'}
                )
                st.plotly_chart(fig_comparativo, use_container_width=True)
            
            with col2:
                # Taxa de poupança
                if total_receitas > 0:
                    taxa_poupanca = (resultado_liquido / total_receitas) * 100
                    st.subheader("💾 Taxa de Poupança")
                    st.metric("Percentual Poupado", f"{taxa_poupanca:.1f}%")
                    
                    # Gauge da taxa de poupança
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = taxa_poupanca,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Taxa de Poupança (%)"},
                        delta = {'reference': 20},
                        gauge = {
                            'axis': {'range': [None, 50]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 10], 'color': "lightgray"},
                                {'range': [10, 20], 'color': "gray"},
                                {'range': [20, 50], 'color': "lightgreen"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 20
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=300)
                    st.plotly_chart(fig_gauge, use_container_width=True)
        
        else:
            st.info("📤 Faça upload de faturas e contracheques para ver o resultado financeiro completo.")
    
    elif opcao == "📋 Transações":
        st.header("📋 Histórico de Transações")
        
        if df_transacoes.empty:
            st.info("📤 Nenhuma transação encontrada. Faça upload de suas faturas.")
            return
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categorias = ['Todas'] + list(df_transacoes['categoria'].unique())
            categoria_filtro = st.selectbox("Filtrar por Categoria", categorias)
        
        with col2:
            cartoes = ['Todos'] + list(df_transacoes['cartao'].unique())
            cartao_filtro = st.selectbox("Filtrar por Cartão", cartoes)
        
        with col3:
            valor_min = st.number_input("Valor Mínimo (R$)", min_value=0.0, value=0.0)
        
        # Aplicar filtros
        df_filtrado = df_transacoes.copy()
        
        if categoria_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
        
        if cartao_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['cartao'] == cartao_filtro]
        
        if valor_min > 0:
            df_filtrado = df_filtrado[df_filtrado['valor'] >= valor_min]
        
        # Mostrar resultados
        st.write(f"📊 Mostrando {len(df_filtrado)} de {len(df_transacoes)} transações")
        
        # Formatação da tabela
        df_display = df_filtrado.copy()
        df_display['valor'] = df_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_display['data'] = pd.to_datetime(df_display['data']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            df_display[['data', 'estabelecimento', 'categoria', 'valor', 'cartao']],
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas do filtro
        if not df_filtrado.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Filtrado", f"R$ {df_filtrado['valor'].sum():,.2f}")
            with col2:
                st.metric("Transações", len(df_filtrado))
            with col3:
                st.metric("Valor Médio", f"R$ {df_filtrado['valor'].mean():,.2f}")
    
    elif opcao == "💵 Receitas":
        st.header("💵 Histórico de Receitas")
        
        if df_receitas.empty:
            st.info("📤 Nenhuma receita encontrada. Faça upload de seus contracheques.")
            return
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categorias_receita = ['Todas'] + list(df_receitas['categoria'].unique())
            categoria_filtro = st.selectbox("Filtrar por Categoria", categorias_receita)
        
        with col2:
            tipos_lancamento = ['Todos', 'credito', 'debito']
            tipo_filtro = st.selectbox("Filtrar por Tipo", tipos_lancamento)
        
        with col3:
            valor_min = st.number_input("Valor Mínimo (R$)", min_value=0.0, value=0.0, key="receitas_valor_min")
        
        # Aplicar filtros
        df_receitas_filtrado = df_receitas.copy()
        
        if categoria_filtro != 'Todas':
            df_receitas_filtrado = df_receitas_filtrado[df_receitas_filtrado['categoria'] == categoria_filtro]
        
        if tipo_filtro != 'Todos':
            df_receitas_filtrado = df_receitas_filtrado[df_receitas_filtrado.get('tipo_lancamento', 'credito') == tipo_filtro]
        
        if valor_min > 0:
            df_receitas_filtrado = df_receitas_filtrado[df_receitas_filtrado['valor'] >= valor_min]
        
        # Mostrar resultados
        st.write(f"📊 Mostrando {len(df_receitas_filtrado)} de {len(df_receitas)} lançamentos")
        
        # Formatação da tabela
        df_receitas_display = df_receitas_filtrado.copy()
        df_receitas_display['valor'] = df_receitas_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_receitas_display['data'] = pd.to_datetime(df_receitas_display['data']).dt.strftime('%d/%m/%Y')
        
        # Verificar colunas existentes
        colunas_exibir = ['data', 'codigo', 'descricao', 'categoria', 'tipo_lancamento', 'valor']
        colunas_disponiveis = verificar_colunas_existem(df_receitas_display, colunas_exibir)
        
        if colunas_disponiveis:
            st.dataframe(
                df_receitas_display[colunas_disponiveis],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(df_receitas_display, use_container_width=True, hide_index=True)
        
        # Estatísticas do filtro
        if not df_receitas_filtrado.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Filtrado", f"R$ {df_receitas_filtrado['valor'].sum():,.2f}")
            with col2:
                st.metric("Lançamentos", len(df_receitas_filtrado))
            with col3:
                st.metric("Valor Médio", f"R$ {df_receitas_filtrado['valor'].mean():,.2f}")
    
    elif opcao == "📁 Arquivos":
        st.header("📁 Arquivos Processados")
        
        if df_arquivos.empty:
            st.info("📤 Nenhum arquivo processado ainda.")
            return
        
        # Estatísticas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_arquivos = len(df_arquivos)
            st.metric("📄 Total de Arquivos", total_arquivos)
        
        with col2:
            faturas_processadas = len(df_arquivos[df_arquivos['tipo_arquivo'] == 'fatura']) if 'tipo_arquivo' in df_arquivos.columns else 0
            st.metric("💳 Faturas Processadas", faturas_processadas)
        
        with col3:
            contracheques_processados = len(df_arquivos[df_arquivos['tipo_arquivo'] == 'contracheque']) if 'tipo_arquivo' in df_arquivos.columns else 0
            st.metric("💰 Contracheques Processados", contracheques_processados)
        
        # Lista de arquivos
        st.subheader("📋 Lista de Arquivos")
        
        for _, arquivo in df_arquivos.iterrows():
            with st.expander(f"📄 {arquivo['nome_arquivo']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Data de Processamento:** {arquivo['data_processamento']}")
                    st.write(f"**Transações Extraídas:** {arquivo['total_transacoes']}")
                with col2:
                    tipo_arquivo = arquivo.get('tipo_arquivo', 'Não especificado')
                    st.write(f"**Tipo:** {tipo_arquivo}")
                    st.write(f"**Hash do Arquivo:** {arquivo['hash_arquivo'][:16]}...")
    
    elif opcao == "⚙️ Configurações":
        st.header("⚙️ Configurações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔄 Atualizar Dashboard")
            if st.button("Recarregar Dados"):
                limpar_cache()
                st.success("✅ Cache limpo! Dados atualizados.")
                st.rerun()
        
        with col2:
            st.subheader("🗑️ Limpar Dados")
            st.warning("⚠️ Esta ação é irreversível!")
            
            if st.button("Limpar Todos os Dados", type="secondary"):
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM transacoes")
                        cursor.execute("DELETE FROM receitas")
                        cursor.execute("DELETE FROM arquivos_processados")
                        conn.commit()
                        limpar_cache()
                        st.success("✅ Todos os dados foram removidos!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao limpar dados: {e}")
                    finally:
                        conn.close()
        
        st.subheader("📊 Informações do Sistema")
        st.info(f"""
        **Versão**: 7.0 (Correção de Ano + Verificação de Colunas)
        **Banco de Dados**: SQLite ({DB_PATH})
        **Tabelas**: transacoes, receitas, arquivos_processados
        **Total de Transações**: {len(df_transacoes)}
        **Total de Receitas**: {len(df_receitas)}
        **Arquivos Processados**: {len(df_arquivos)}
        **Códigos de Crédito**: {', '.join(CODIGOS_CREDITO)}
        """)

if __name__ == "__main__":
    main()

