# AI Business Agent

Protótipo de análise empresarial com agentes de IA, dashboard e integração Shopify em desenvolvimento.

## Demonstração pública no navegador

[Abrir o Laboratório de receita](https://babeto-revenue-demo.ruraltapir1.chatgpt.site/)

Explore o cenário de receita alterando pedidos fictícios. Acesso sem login, instalação ou conta Shopify. Esta demonstração educacional apresenta apenas o cálculo ilustrativo; não é o dashboard completo nem uma previsão por IA.

## Experimentar sem loja Shopify

**Protótipo em desenvolvimento.** A demonstração abaixo usa dados fictícios e não exige conta Shopify, banco de dados, credenciais ou serviços pagos. Ela demonstra o cálculo do cenário de receita; não abre o dashboard completo.

Na raiz do repositório, com Python 3.10 ou superior:

```bash
python -m examples.revenue_demo
```

Resultado: R$ 1.600,00 em pedidos fictícios, média recente de R$ 200,00 e cenário de R$ 1.800,00 com um pedido hipotético adicional. Não é previsão por IA ou crescimento mensal.

Veja [o guia da demonstração](docs/demonstracao-sem-shopify.md).

### Testes offline

Com Python 3.12, em um ambiente virtual:

```bash
python -m pip install "pandas==2.2.3"
python -m unittest discover -s tests -v
```

Os 14 testes cobrem cálculo monetário, apresentação e sincronização simulada. O workflow `Offline revenue checks` executa os testes e a demonstração com pandas 2.2.3 (ambiente local verificado) e 3.0.2 (versão declarada em `requirements.txt`). O resultado remoto deve ser conferido na aba Actions.

A integração Shopify real, a persistência real e o dashboard completo ainda não foram validados ponta a ponta. As demais seções descrevem componentes e configuração do protótipo, não uma certificação de prontidão comercial.



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
- Segmento Shopify com maior receita
- Segmento Shopify em revisão operacional
- Cenário ilustrativo de receita com um pedido hipotético adicional

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
- Segmentos Shopify estratégicos
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

Há um módulo experimental com regressão linear. Ele ainda não foi validado como previsão temporal e não fundamenta o cenário de receita do dashboard.

---

## Chat Empresarial IA

Permite perguntas como:

- "Faça uma análise estratégica"
- "Qual segmento Shopify apresenta maior crescimento?"
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
PLATFORM_ADMIN_EMAIL=admin@suaempresa.com
```

## SaaS Multi-Cliente

O primeiro cliente e o primeiro administrador sao criados automaticamente a partir das variaveis `BOOTSTRAP_TENANT_*` e `BOOTSTRAP_ADMIN_*`.

Depois do primeiro login, apenas o email configurado em `PLATFORM_ADMIN_EMAIL` pode cadastrar novos clientes SaaS e visualizar o resumo comercial global pelo dashboard. Cada cliente acessa somente a propria empresa.

## Trial e cobranca internacional com Paddle

Cada novo cliente recebe 14 dias gratis, sem cartao. Quando o trial termina, analises premium e sincronizacoes automaticas ficam pausadas ate a ativacao de uma assinatura.

Para habilitar cobrancas reais, use a Paddle como Merchant of Record. Crie os tres precos mensais recorrentes na Paddle e configure:

```env
PADDLE_ENVIRONMENT=sandbox
PADDLE_API_KEY=pdl_sdbx_apikey_...
PADDLE_WEBHOOK_SECRET=pdl_ntfset_...
PADDLE_PRICE_REVENUE_INTELLIGENCE=pri_...
PADDLE_PRICE_GROWTH_INTELLIGENCE=pri_...
PADDLE_PRICE_REVENUE_OS=pri_...
```

Na Paddle, configure um webhook:

```text
https://seu-dominio-api.com/billing/webhook
```

Eventos necessarios:

```text
subscription.created
subscription.updated
subscription.canceled
```

Antes do checkout real, configure tambem o `Default payment link` nas configuracoes de checkout da Paddle. Use `PADDLE_ENVIRONMENT=production` somente depois da aprovacao da conta e dos testes no sandbox.

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

Os módulos de machine learning são experimentais. O cenário exibido no dashboard usa receita importada mais a média de até três pedidos recentes, sem horizonte de previsão.

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
