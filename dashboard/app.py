import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
from openai import OpenAI


st.set_page_config(
    page_title="AI Business Agent",
    layout="wide"
)


PRIMARY_BLUE = "#16324F"
SECONDARY_BLUE = "#1F4E79"
CORPORATE_GREEN = "#2E7D32"
DARK_GREEN = "#1B5E20"
LIGHT_BACKGROUND = "#F5F7FA"
SIDEBAR_BACKGROUND = "#EEF3F0"
CARD_BORDER = "#D9E2EC"
TEXT_COLOR = "#1F2937"
SOFT_BLUE = "#EAF2F8"

CHART_COLORS = [
    "#16324F",
    "#1F4E79",
    "#2F75B5",
    "#548235",
    "#70AD47",
    "#A5A5A5",
    "#264478",
]

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {LIGHT_BACKGROUND};
    }}

    .block-container {{
        padding-top: 2.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    h1 {{
        color: {PRIMARY_BLUE};
        font-family: Arial, sans-serif;
        font-size: 2.35rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }}

    h2, h3 {{
        color: {TEXT_COLOR};
        font-family: Arial, sans-serif;
        font-weight: 650;
    }}

    p, div, span, label {{
        font-family: Arial, sans-serif;
    }}

    hr {{
        margin-top: 1.8rem;
        margin-bottom: 1.8rem;
        border-color: #E5E7EB;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BACKGROUND};
        border-right: 1px solid #D5DED8;
    }}

    section[data-testid="stSidebar"] .stButton button {{
        background-color: {PRIMARY_BLUE} !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.1rem !important;
    }}

    section[data-testid="stSidebar"] .stButton button:hover {{
        background-color: {SECONDARY_BLUE} !important;
        color: #FFFFFF !important;
    }}

    div[data-baseweb="tag"] {{
        background-color: {SECONDARY_BLUE} !important;
        border-radius: 7px !important;
        border: none !important;
        padding: 3px 7px !important;
    }}

    div[data-baseweb="tag"] span {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }}

    div[data-baseweb="tag"] svg {{
        color: #FFFFFF !important;
    }}

    div[data-baseweb="select"] svg {{
        color: {SECONDARY_BLUE} !important;
    }}

    .stSlider > div > div > div > div {{
        background-color: {CORPORATE_GREEN} !important;
    }}

    .stSlider [role="slider"] {{
        background-color: {CORPORATE_GREEN} !important;
        border: 3px solid {DARK_GREEN} !important;
    }}

    .stMetric {{
        background-color: #FFFFFF;
        padding: 1.35rem;
        border-radius: 12px;
        border: 1px solid {CARD_BORDER};
        border-left: 5px solid {CORPORATE_GREEN};
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    }}

    .stButton button {{
        background-color: {SECONDARY_BLUE};
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }}

    .stButton button:hover {{
        background-color: {PRIMARY_BLUE};
        color: #FFFFFF;
    }}

    div[data-testid="stAlert"] {{
        background-color: {SOFT_BLUE} !important;
        color: {PRIMARY_BLUE} !important;
        border: 1px solid #BFD7EA !important;
        border-radius: 10px !important;
    }}

    section[data-testid="stFileUploader"] {{
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid {CARD_BORDER};
        padding: 1rem;
    }}

    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {CARD_BORDER};
    }}

    textarea, input {{
        border-radius: 8px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR CORPORATIVA
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding-top:10px; padding-bottom:20px;">
            <h1 style="
                color:#16324F;
                font-size:28px;
                margin-bottom:0;
                font-weight:700;
            ">
                AI Business
            </h1>
            <p style="
                color:#64748B;
                margin-top:0;
                font-size:14px;
            ">
                Enterprise Analytics Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


# =========================================================
# LOGIN
# =========================================================

hashed_password = stauth.Hasher.hash("admin123")

credentials = {
    "usernames": {
        "admin": {
            "name": "Administrador",
            "password": hashed_password,
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "ai_business_dashboard",
    "ai_business_auth_key",
    cookie_expiry_days=30,
)

login_result = authenticator.login(location="main")

if isinstance(login_result, tuple):
    name, authentication_status, username = login_result
else:
    name = st.session_state.get("name")
    authentication_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")

if authentication_status is False:
    st.info("Usuario ou senha incorretos.")
    st.stop()

if authentication_status is None:
    st.info("Digite seu usuario e senha para acessar o painel.")
    st.stop()

authenticator.logout("Sair", "sidebar")
st.sidebar.success(f"Bem-vinda, {name}")


# =========================================================
# CABECALHO
# =========================================================

st.title("Painel de controle do agente de negocios com IA")

st.markdown(
    """
    Painel corporativo de Business Intelligence para monitoramento de vendas,
    analise de desempenho por setor, upload de CSV, filtros interativos,
    analise executiva com IA e assistente empresarial.
    """
)


# =========================================================
# ARQUIVOS E AMBIENTE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "vendas.csv"

load_dotenv(BASE_DIR / ".env")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


# =========================================================
# FONTE DE DADOS
# =========================================================

st.divider()

st.subheader("Fonte de dados")

uploaded_file = st.file_uploader(
    "Faca upload de um arquivo CSV de vendas.",
    type=["csv"],
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    if not DATA_PATH.exists():
        st.info(f"Arquivo nao encontrado: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)


# =========================================================
# VALIDACAO DOS DADOS
# =========================================================

required_columns = {"setor", "vendas"}

if not required_columns.issubset(df.columns):
    st.info("O CSV precisa conter as colunas: setor e vendas.")
    st.stop()

df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")
df = df.dropna(subset=["setor", "vendas"])

if df.empty:
    st.info("O conjunto de dados esta vazio ou contem dados invalidos.")
    st.stop()


# =========================================================
# FILTROS
# =========================================================

st.sidebar.markdown(
    """
    <h2 style="
        color:#16324F;
        font-size:24px;
        font-weight:700;
        margin-bottom:20px;
    ">
        Filtros estrategicos
    </h2>
    """,
    unsafe_allow_html=True,
)

selected_sectors = st.sidebar.multiselect(
    "Selecione os setores",
    options=sorted(df["setor"].unique()),
    default=sorted(df["setor"].unique()),
)

min_revenue = int(df["vendas"].min())
max_revenue = int(df["vendas"].max())

selected_min_revenue = st.sidebar.slider(
    "Receita minima",
    min_revenue,
    max_revenue,
    min_revenue,
)

filtered_df = df[
    (df["setor"].isin(selected_sectors))
    & (df["vendas"] >= selected_min_revenue)
]

if filtered_df.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()


# =========================================================
# METRICAS
# =========================================================

total_sales = filtered_df["vendas"].sum()
average_sales = filtered_df["vendas"].mean()

best_sector = filtered_df.loc[filtered_df["vendas"].idxmax(), "setor"]
lowest_sector = filtered_df.loc[filtered_df["vendas"].idxmin(), "setor"]

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Receita Total", f"R$ {total_sales:,.2f}", border=True)
col2.metric("Receita Media", f"R$ {average_sales:,.2f}", border=True)
col3.metric("Melhor Setor", best_sector, border=True)
col4.metric("Setor Critico", lowest_sector, border=True)


# =========================================================
# GRAFICO E SUMARIO EXECUTIVO
# =========================================================

st.divider()

left_col, right_col = st.columns([2.2, 1])

with left_col:
    st.subheader("Desempenho de vendas por setor")

    chart = px.bar(
        filtered_df,
        x="setor",
        y="vendas",
        color="setor",
        text_auto=True,
        title="Receita por setor",
        color_discrete_sequence=CHART_COLORS,
        labels={
            "setor": "Setor",
            "vendas": "Receita",
        },
    )

    chart.update_traces(
        textposition="inside",
        textfont=dict(
            color="white",
            size=13,
        ),
        marker_line_color="#FFFFFF",
        marker_line_width=1.5,
    )

    chart.update_layout(
        showlegend=False,
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#F8FAFC",
        font=dict(
            family="Arial",
            color=TEXT_COLOR,
        ),
        title=dict(
            x=0.01,
            font=dict(
                size=18,
                color=PRIMARY_BLUE,
            ),
        ),
        xaxis=dict(
            title="Setor",
            showgrid=False,
            linecolor="#CBD5E1",
        ),
        yaxis=dict(
            title="Receita",
            gridcolor="#E5E7EB",
            linecolor="#CBD5E1",
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )

    st.plotly_chart(chart, use_container_width=True)

with right_col:
    st.subheader("Sumario executivo")

    st.write(
        f"""
        O setor de melhor desempenho e **{best_sector}**, representando a maior contribuicao para a receita.

        O setor com menor desempenho e **{lowest_sector}**, indicando uma oportunidade para revisao comercial e operacional.

        A receita total analisada atingiu **R$ {total_sales:,.2f}**.
        """
    )


# =========================================================
# TABELA DE DADOS
# =========================================================

st.divider()

st.subheader("Conjunto de dados de vendas")

st.dataframe(filtered_df, use_container_width=True)


# =========================================================
# RECOMENDACOES
# =========================================================

st.divider()

st.subheader("Recomendacoes de negocios")

st.info(
    f"""
    Proximos passos recomendados:

    1. Investigar os fatores que impulsionam o desempenho do setor de {best_sector}.
    2. Revisar a estrategia comercial do setor de {lowest_sector}.
    3. Expandir os dados com custos, margens, datas e segmentos de clientes.
    4. Aplicar modelos preditivos para projecoes futuras.
    """
)


# =========================================================
# ANALISE EXECUTIVA COM IA
# =========================================================

st.divider()

st.subheader("Analise executiva de IA")

if client is None:
    st.info("OPENAI_API_KEY nao encontrada no arquivo .env.")
else:
    data_text = filtered_df.to_string(index=False)

    executive_prompt = f"""
    Voce e um consultor executivo especialista em Business Intelligence.

    Analise os dados abaixo e gere:

    1. Resumo executivo
    2. Melhor setor
    3. Pior setor
    4. Insights estrategicos
    5. Recomendacoes empresariais

    Dados:

    {data_text}
    """

    if st.button("Gerar analise de IA"):
        with st.spinner("Gerando analise executiva..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Voce e um consultor executivo especialista em analise de negocios.",
                    },
                    {
                        "role": "user",
                        "content": executive_prompt,
                    },
                ],
                temperature=0.5,
            )

            analysis = response.choices[0].message.content

            st.success("Analise gerada com sucesso.")
            st.markdown(analysis)


# =========================================================
# ASSISTENTE DE IA
# =========================================================

st.divider()

st.subheader("Assistente de IA")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_question = st.text_area(
    "Faca uma pergunta sobre os dados empresariais:",
    placeholder="Exemplo: Qual setor merece mais investimento?",
)

if st.button("Consultar IA"):
    if client is None:
        st.info("Adicione sua chave OPENAI_API_KEY no arquivo .env.")

    elif user_question.strip() == "":
        st.info("Digite uma pergunta.")

    else:
        business_context = filtered_df.to_string(index=False)

        assistant_prompt = f"""
        Voce e um especialista em Business Intelligence.

        Responda a pergunta do usuario utilizando os dados abaixo.

        Dados:

        {business_context}

        Pergunta:

        {user_question}
        """

        with st.spinner("Consultando IA..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Voce e um especialista em analise empresarial.",
                    },
                    {
                        "role": "user",
                        "content": assistant_prompt,
                    },
                ],
                temperature=0.5,
            )

            answer = response.choices[0].message.content

            st.session_state.chat_history.append(
                {
                    "pergunta": user_question,
                    "resposta": answer,
                }
            )

            st.success("Resposta gerada com sucesso.")

if st.session_state.chat_history:
    st.subheader("Historico de conversa")

    for item in reversed(st.session_state.chat_history):
        st.markdown("---")
        st.markdown("**Pergunta**")
        st.write(item["pergunta"])
        st.markdown("**Resposta da IA**")
        st.markdown(item["resposta"])