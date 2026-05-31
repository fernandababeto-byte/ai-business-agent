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
POSTGRES_PASSWORD=uma_senha_forte
JWT_SECRET_KEY=um_segredo_forte
BOOTSTRAP_ADMIN_EMAIL=admin@suaempresa.com
BOOTSTRAP_ADMIN_PASSWORD=uma_senha_forte
```

## SaaS Multi-Cliente

O primeiro cliente e o primeiro administrador sao criados automaticamente a partir das variaveis `BOOTSTRAP_TENANT_*` e `BOOTSTRAP_ADMIN_*`.

Depois do primeiro login, usuarios com papel `owner` ou `admin` podem cadastrar novos clientes SaaS pelo dashboard.

## Shopify OAuth

Para conectar lojas reais, crie um app no Shopify Partner Dashboard e configure no `.env`:

```env
SHOPIFY_CLIENT_ID=sua_client_id
SHOPIFY_CLIENT_SECRET=sua_client_secret
SHOPIFY_APP_URL=https://seu-dominio-api.com
DASHBOARD_URL=https://seu-dashboard.com
SHOPIFY_SCOPES=read_orders,read_products,read_inventory,read_locations,read_customers
```

No app da Shopify, configure a URL de callback:

```text
https://seu-dominio-api.com/shopify/callback
```

Em desenvolvimento local, o callback `http://localhost:8000/shopify/callback` so funciona se a Shopify conseguir acessar sua maquina via tunel publico.

## Deploy de teste gratuito no Render

O arquivo `render.yaml` cria dois Web Services gratuitos e um Postgres gratuito:

- `revenue-os-api`
- `revenue-os-dashboard`
- `revenue-os-db`

O deploy gratuito serve para testes online. Os Web Services gratuitos podem hibernar quando ficam sem uso e o Postgres gratuito expira apos 30 dias. Antes de receber clientes pagantes, migre para instancias pagas e configure um dominio proprio.

No Render, crie um Blueprint a partir deste repositorio. Durante a criacao, preencha:

```text
DASHBOARD_URL=https://revenue-os-dashboard.onrender.com
SHOPIFY_APP_URL=https://revenue-os-api.onrender.com
API_BASE_URL=https://revenue-os-api.onrender.com
```

Preencha tambem as credenciais Shopify, Resend, Twilio e o primeiro administrador. Nunca coloque segredos diretamente no arquivo `render.yaml`.

Depois que o deploy terminar, crie uma nova versao do app no Shopify Dev Dashboard com:

```text
URL do app: https://revenue-os-api.onrender.com
URL de redirecionamento: https://revenue-os-api.onrender.com/shopify/callback
```

Por fim, abra:

```text
https://revenue-os-dashboard.onrender.com
```

## Planos SaaS

O produto deve ser posicionado como um AI Revenue Operating System premium para Shopify. Nao existe plano abaixo de US$99/mes.

- Revenue Intelligence: US$99/mes, com dashboard executivo, monitoring, risk center, revenue advisor e forecast engine.
- Growth Intelligence: US$199/mes, com alertas automaticos, relatorios executivos, monitoring avancado e priorizacao de oportunidades.
- Revenue OS: US$399/mes, com multi-store Shopify, executive reports, recomendacoes avancadas e suporte prioritario.

Trial padrao: 14 dias gratis, sem cartao.

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
