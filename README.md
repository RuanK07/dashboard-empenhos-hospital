# Dashboard de Empenhos - Hospital Público

## Descrição

Este é um dashboard interativo desenvolvido em Streamlit para visualizar e analisar dados de empenhos de um hospital público. O sistema oferece uma interface moderna e responsiva para acesso via web e dispositivos móveis.

## Funcionalidades

### 📊 Visualizações Interativas
- Gráficos de barras por setor
- Gráfico de pizza das top 10 empresas
- Evolução temporal dos empenhos
- Distribuição de valores
- Análise trimestral

### 🔍 Filtros Avançados
- Filtro por setor
- Filtro por empresa
- Filtro por ano e mês
- Filtro por faixa de valor
- Busca por texto (empresa ou contrato)

### 📋 Funcionalidades Adicionais
- Métricas em tempo real
- Tabela de dados detalhados
- Download de dados filtrados em CSV
- Alertas para contratos próximos ao vencimento
- Análise de concentração de gastos
- Interface responsiva para mobile

## Estrutura do Projeto

```
/
├── dashboard_enhanced.py    # Aplicação principal do Streamlit
├── processed_data.csv      # Dados processados da planilha
├── requirements.txt        # Dependências do projeto
└── README.md              # Documentação
```

## Como Executar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o dashboard:
```bash
streamlit run dashboard_enhanced.py --server.port 8501 --server.address 0.0.0.0
```

3. Acesse no navegador: `http://localhost:8501`

## Dados

O dashboard utiliza dados de empenhos do hospital público com as seguintes informações:
- Item e setor
- Empresa contratada
- Valor do empenho
- Data de competência
- Número do contrato
- Data de vencimento
- E outras informações administrativas

## Tecnologias Utilizadas

- **Streamlit**: Framework para criação de aplicações web
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas
- **Python**: Linguagem de programação

## Autor

Desenvolvido para o sistema de gestão de empenhos do hospital público.

