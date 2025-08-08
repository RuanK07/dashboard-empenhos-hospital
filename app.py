import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Empenhos - Hospital Público",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para estilização moderna e responsiva
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    .search-box {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        .main-header h1 {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('processed_data.csv')
        # Converter colunas de data
        df['COMPETENCIA'] = pd.to_datetime(df['COMPETENCIA'], errors='coerce')
        df['VENCIMENTO_CONTRATO'] = pd.to_datetime(df['VENCIMENTO_CONTRATO'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = load_data()

if df.empty:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo processed_data.csv existe.")
    st.stop()

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🏥 Dashboard de Empenhos - Hospital Público</h1>
    <p>Sistema de Gestão e Controle de Empenhos 2025</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por setor
setores = ['Todos'] + sorted(df['SETOR'].dropna().unique().tolist())
setor_selecionado = st.sidebar.selectbox("Selecione o Setor:", setores)

# Filtro por empresa
empresas = ['Todas'] + sorted(df['EMPRESA'].dropna().unique().tolist())
empresa_selecionada = st.sidebar.selectbox("Selecione a Empresa:", empresas)

# Filtro por mês/ano
if 'COMPETENCIA' in df.columns and not df['COMPETENCIA'].isna().all():
    anos_disponiveis = sorted(df['COMPETENCIA'].dt.year.dropna().unique())
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", ['Todos'] + [int(ano) for ano in anos_disponiveis])
    
    meses_disponiveis = sorted(df['COMPETENCIA'].dt.month.dropna().unique())
    mes_selecionado = st.sidebar.selectbox("Selecione o Mês:", ['Todos'] + [int(mes) for mes in meses_disponiveis])
else:
    ano_selecionado = 'Todos'
    mes_selecionado = 'Todos'

# Filtro por faixa de valor
st.sidebar.subheader("💰 Faixa de Valor")
valor_min = float(df['VALOR'].min())
valor_max = float(df['VALOR'].max())
faixa_valor = st.sidebar.slider(
    "Selecione a faixa de valor:",
    min_value=valor_min,
    max_value=valor_max,
    value=(valor_min, valor_max),
    format="R$ %.2f"
)

# Busca por texto
st.sidebar.subheader("🔍 Busca")
termo_busca = st.sidebar.text_input("Buscar por empresa ou contrato:")

# Aplicar filtros
df_filtrado = df.copy()

if setor_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['SETOR'] == setor_selecionado]

if empresa_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['EMPRESA'] == empresa_selecionada]

if ano_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['COMPETENCIA'].dt.year == ano_selecionado]

if mes_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['COMPETENCIA'].dt.month == mes_selecionado]

# Filtro por faixa de valor
df_filtrado = df_filtrado[
    (df_filtrado['VALOR'] >= faixa_valor[0]) & 
    (df_filtrado['VALOR'] <= faixa_valor[1])
]

# Filtro por busca de texto
if termo_busca:
    mask = (
        df_filtrado['EMPRESA'].str.contains(termo_busca, case=False, na=False) |
        df_filtrado['CONTRATO'].str.contains(termo_busca, case=False, na=False)
    )
    df_filtrado = df_filtrado[mask]

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_empenhos = len(df_filtrado)
    st.metric("Total de Empenhos", f"{total_empenhos:,}")

with col2:
    valor_total = df_filtrado['VALOR'].sum()
    st.metric("Valor Total", f"R$ {valor_total:,.2f}")

with col3:
    empresas_unicas = df_filtrado['EMPRESA'].nunique()
    st.metric("Empresas Únicas", empresas_unicas)

with col4:
    setores_unicos = df_filtrado['SETOR'].nunique()
    st.metric("Setores Únicos", setores_unicos)

# Abas para diferentes visualizações
tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📈 Análise Temporal", "🏢 Empresas", "📋 Dados Detalhados"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Empenhos por Setor")
        if not df_filtrado.empty:
            empenhos_setor = df_filtrado.groupby('SETOR')['VALOR'].sum().sort_values(ascending=False)
            fig_setor = px.bar(
                x=empenhos_setor.values,
                y=empenhos_setor.index,
                orientation='h',
                title="Valor Total por Setor",
                labels={'x': 'Valor (R$)', 'y': 'Setor'},
                color=empenhos_setor.values,
                color_continuous_scale='Blues'
            )
            fig_setor.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_setor, use_container_width=True)

    with col2:
        st.subheader("📈 Top 10 Empresas")
        if not df_filtrado.empty:
            top_empresas = df_filtrado.groupby('EMPRESA')['VALOR'].sum().sort_values(ascending=False).head(10)
            fig_empresas = px.pie(
                values=top_empresas.values,
                names=top_empresas.index,
                title="Top 10 Empresas por Valor"
            )
            fig_empresas.update_layout(height=400)
            st.plotly_chart(fig_empresas, use_container_width=True)

    # Distribuição de valores
    st.subheader("💰 Distribuição de Valores")
    if not df_filtrado.empty:
        fig_hist = px.histogram(
            df_filtrado,
            x='VALOR',
            nbins=30,
            title="Distribuição dos Valores dos Empenhos",
            labels={'VALOR': 'Valor (R$)', 'count': 'Frequência'}
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    if 'COMPETENCIA' in df_filtrado.columns and not df_filtrado['COMPETENCIA'].isna().all():
        st.subheader("📅 Evolução Temporal dos Empenhos")
        
        # Evolução mensal
        evolucao_temporal = df_filtrado.groupby(df_filtrado['COMPETENCIA'].dt.to_period('M'))['VALOR'].sum()
        
        fig_temporal = px.line(
            x=evolucao_temporal.index.astype(str),
            y=evolucao_temporal.values,
            title="Evolução dos Valores por Mês",
            labels={'x': 'Mês/Ano', 'y': 'Valor (R$)'}
        )
        fig_temporal.update_layout(height=400)
        st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Análise por trimestre
        st.subheader("📊 Análise Trimestral")
        df_filtrado['Trimestre'] = df_filtrado['COMPETENCIA'].dt.to_period('Q')
        trimestre_data = df_filtrado.groupby('Trimestre')['VALOR'].sum()
        
        fig_trimestre = px.bar(
            x=trimestre_data.index.astype(str),
            y=trimestre_data.values,
            title="Valores por Trimestre",
            labels={'x': 'Trimestre', 'y': 'Valor (R$)'}
        )
        fig_trimestre.update_layout(height=400)
        st.plotly_chart(fig_trimestre, use_container_width=True)

with tab3:
    st.subheader("🏢 Análise Detalhada de Empresas")
    
    # Ranking de empresas
    ranking_empresas = df_filtrado.groupby('EMPRESA').agg({
        'VALOR': ['sum', 'count', 'mean']
    }).round(2)
    ranking_empresas.columns = ['Valor Total', 'Quantidade', 'Valor Médio']
    ranking_empresas = ranking_empresas.sort_values('Valor Total', ascending=False)
    
    st.dataframe(ranking_empresas.head(20), use_container_width=True)
    
    # Análise de concentração
    st.subheader("📊 Concentração de Gastos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 empresas vs resto
        top5_empresas = ranking_empresas.head(5)['Valor Total'].sum()
        resto_empresas = ranking_empresas.tail(-5)['Valor Total'].sum()
        
        fig_concentracao = px.pie(
            values=[top5_empresas, resto_empresas],
            names=['Top 5 Empresas', 'Demais Empresas'],
            title="Concentração de Gastos - Top 5 vs Demais"
        )
        st.plotly_chart(fig_concentracao, use_container_width=True)
    
    with col2:
        # Empresas por setor
        empresas_setor = df_filtrado.groupby('SETOR')['EMPRESA'].nunique().sort_values(ascending=False)
        fig_emp_setor = px.bar(
            x=empresas_setor.values,
            y=empresas_setor.index,
            orientation='h',
            title="Número de Empresas por Setor"
        )
        st.plotly_chart(fig_emp_setor, use_container_width=True)

with tab4:
    st.subheader("📋 Dados Detalhados")
    
    # Opções de visualização
    col1, col2, col3 = st.columns(3)
    with col1:
        mostrar_linhas = st.selectbox("Linhas por página:", [50, 100, 200, 500])
    with col2:
        ordenar_por = st.selectbox("Ordenar por:", ['VALOR', 'COMPETENCIA', 'EMPRESA', 'SETOR'])
    with col3:
        ordem = st.selectbox("Ordem:", ['Decrescente', 'Crescente'])
    
    # Preparar dados para exibição
    colunas_exibir = ['ITEM', 'SETOR', 'EMPRESA', 'VALOR', 'COMPETENCIA', 'CONTRATO']
    colunas_disponiveis = [col for col in colunas_exibir if col in df_filtrado.columns]
    
    if colunas_disponiveis:
        df_exibir = df_filtrado[colunas_disponiveis].copy()
        
        # Aplicar ordenação
        ascending = ordem == 'Crescente'
        df_exibir = df_exibir.sort_values(ordenar_por, ascending=ascending)
        
        # Formatar valores monetários
        if 'VALOR' in df_exibir.columns:
            df_exibir['VALOR'] = df_exibir['VALOR'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(
            df_exibir.head(mostrar_linhas),
            use_container_width=True,
            height=400
        )
        
        # Botão para download
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Baixar dados filtrados (CSV)",
            data=csv,
            file_name=f"empenhos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Colunas necessárias não encontradas nos dados.")

# Informações adicionais na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Resumo dos Filtros")
st.sidebar.write(f"**Registros exibidos:** {len(df_filtrado):,}")
st.sidebar.write(f"**Total de registros:** {len(df):,}")

if not df_filtrado.empty:
    st.sidebar.write(f"**Valor médio:** R$ {df_filtrado['VALOR'].mean():,.2f}")
    st.sidebar.write(f"**Valor máximo:** R$ {df_filtrado['VALOR'].max():,.2f}")
    st.sidebar.write(f"**Valor mínimo:** R$ {df_filtrado['VALOR'].min():,.2f}")

# Alertas e insights
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Alertas")

# Contratos próximos ao vencimento
if 'VENCIMENTO_CONTRATO' in df_filtrado.columns:
    hoje = pd.Timestamp.now()
    proximos_vencimento = df_filtrado[
        (df_filtrado['VENCIMENTO_CONTRATO'] > hoje) & 
        (df_filtrado['VENCIMENTO_CONTRATO'] <= hoje + pd.Timedelta(days=30))
    ]
    
    if not proximos_vencimento.empty:
        st.sidebar.warning(f"⚠️ {len(proximos_vencimento)} contratos vencem em 30 dias")

# Valores altos
valor_alto_threshold = df_filtrado['VALOR'].quantile(0.95)
valores_altos = df_filtrado[df_filtrado['VALOR'] > valor_alto_threshold]

if not valores_altos.empty:
    st.sidebar.info(f"💰 {len(valores_altos)} empenhos com valores acima do percentil 95")

