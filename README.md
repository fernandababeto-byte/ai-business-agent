# AI Business Agent

Plataforma corporativa de Inteligência Artificial para análise estratégica empresarial, automação executiva, previsão de vendas e suporte à tomada de decisão.

---

# Visão Geral

O AI Business Agent é uma plataforma empresarial construída com:

- FastAPI
- Streamlit
- OpenAI API
- Groq API
- Machine Learning
- Multiagentes de IA
- Business Intelligence
- Geração de PDF
- Dashboard executivo

O sistema foi desenvolvido para transformar dados empresariais em insights estratégicos automatizados utilizando Inteligência Artificial.

---

# Funcionalidades

## Dashboard Corporativo

- KPIs empresariais
- Receita total
- Receita média
- Melhor setor
- Setor crítico
- Previsão inteligente de vendas

---

## Upload de Dados

Suporte para:

- CSV
- Excel (.xlsx)

---

## Inteligência Artificial

### Agente Executivo

Gera:

- Relatórios estratégicos
- Insights empresariais
- Recomendações executivas
- Análise corporativa

---

### Agente Comercial

Analisa:

- Performance de vendas
- Setores estratégicos
- Crescimento comercial
- Oportunidades de mercado

---

### Agente Financeiro

Analisa:

- Receita
- Tendências financeiras
- Indicadores econômicos
- Performance financeira

---

## Machine Learning

Sistema de previsão inteligente utilizando:

- Linear Regression
- Forecast de vendas
- Tendência empresarial

---

## Chat Empresarial IA

Permite perguntas como:

- "Faça uma análise estratégica"
- "Qual setor apresenta maior crescimento?"
- "Crie um resumo executivo"
- "Analise os dados financeiros"

---

## PDF Executivo

Geração automática de:

- Relatórios empresariais
- PDFs corporativos
- Insights estratégicos
- Recomendações executivas

---

# Tecnologias Utilizadas

## Backend

- FastAPI
- Python

## Frontend

- Streamlit

## Inteligência Artificial

- OpenAI API
- Groq API

## Machine Learning

- Scikit-learn
- Pandas

## Visualização

- Plotly

## Relatórios

- ReportLab

---

# Estrutura do Projeto

```bash
ai-business-agent/
│
├── agents/
│   ├── executive_agent.py
│   ├── finance_agent.py
│   ├── sales_agent.py
│   └── support_agent.py
│
├── api/
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   └── vendas.csv
│
├── memory/
│   └── chat_history.csv
│
├── ml/
│   ├── sales_forecast.py
│   └── forecast_chart.py
│
├── reports/
│
├── services/
│   ├── openai_service.py
│   ├── groq_service.py
│   └── pdf_service.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# Instalação

## Clone o projeto

```bash
git clone https://github.com/fernandababeto-byte/ai-business-agent.git
```

---

## Entre na pasta

```bash
cd ai-business-agent
```

---

## Crie ambiente virtual

```bash
python -m venv venv
```

---

## Ative o ambiente virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## Instale dependências

```bash
pip install -r requirements.txt
```

---

# Configuração das APIs

Crie um arquivo `.env`

```env
OPENAI_API_KEY=sua_chave_openai
GROQ_API_KEY=sua_chave_groq
```

---

# Executando o Backend

```bash
uvicorn api.main:app --reload
```

Swagger:

```bash
http://127.0.0.1:8000/docs
```

---

# Executando o Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard:

```bash
http://localhost:8501
```

---

# Machine Learning

O sistema possui:

- Forecast de vendas
- Predição de receita
- Tendência temporal
- Análise estatística

---

# Segurança

- Variáveis protegidas via `.env`
- `.gitignore` configurado
- APIs isoladas
- Controle de autenticação

---

# Roadmap

## Próximas versões

- Deploy cloud
- Multiusuário
- Banco de dados
- Docker
- Kubernetes
- SaaS
- Login empresarial
- BI avançado
- Agentes autônomos
- Integração ERP/CRM
- API comercial

---

# Objetivo do Projeto

Transformar Inteligência Artificial em uma plataforma empresarial capaz de:

- Automatizar análises executivas
- Apoiar decisões estratégicas
- Gerar insights inteligentes
- Escalar operações empresariais

---

# Desenvolvedora

Fernanda Babeto

- Inteligência Artificial
- Machine Learning
- Business Intelligence
- Multiagentes IA
- Automação Empresarial

GitHub:

https://github.com/fernandababeto-byte

---

# Licença

MIT License
