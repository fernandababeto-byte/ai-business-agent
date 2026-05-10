import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="AI Business Agent",
    layout="wide"
)

# =========================================================
# ESTILO PROFISSIONAL CORPORATIVO
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f4f7f5;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: #16324f;
        font-family: Arial, sans-serif;
        font-weight: 700;
    }

    h2, h3 {
        color: #1f2937;
        font-family: Arial, sans-serif;
        font-weight: 600;
    }

    p, div, span, label {
        font-family: Arial, sans-serif;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background-color: #eef4ef;
        border-right: 1px solid #d6e2d8;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #1f2937;
    }

    /* MULTISELECT - BOTÕES DOS SETORES */

    div[data-baseweb="tag"] {
        background-color: #1f4e79 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 2px 6px !important;
    }

    div[data-baseweb="tag"] span {
        color: #ffffff !important;
        font-weight: 600;
        font-size: 14px !important;
    }

    div[data-baseweb="select"] svg {
        color: #1f4e79 !important;
    }

    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    /* SLIDER */

    .stSlider > div > div > div > div {
        background-color: #2e7d32 !important;
    }

    .stSlider [role="slider"] {
        background-color: #2e7d32 !important;
        border: 3px solid #1b5e20 !important;
        width: 18px !important;
        height: 18px !important;
    }

    .stSlider label {
        color: #1f2937 !important;
        font-weight: 600;
    }

    /* MÉTRICAS */

    .stMetric {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* BOTÕES PRINCIPAIS */

    .stButton button {
        background-color: #1f4e79;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }

    .stButton button:hover {
        background-color: #16324f;
        color: white;
    }

    /* FILE UPLOADER */

    section[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        padding: 1rem;
    }

    /* DATAFRAME */

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ALERTAS */

    .stAlert {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TÍTULO
# =========================================================

st.title("Painel de controle do agente de negócios com IA")

st.markdown(
    """
    Painel de Business Intelligence profissional para monitoramento de vendas,
    análise de desempenho do setor, upload de CSV, filtros interativos,
    análise executiva com IA e assistente corporativo.
    """
)

# =========================================================
# LOCALIZAÇÃO DOS ARQUIVOS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "vendas.csv"

# =========================================================
# UPLOAD DE CSV
# =========================================================

st.divider()

st.subheader("Fonte de dados")

uploaded_file = st.file_uploader(
    "Faça upload de um arquivo CSV de vendas.",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:

    if not DATA_PATH.exists():
        st.error(f"Arquivo não encontrado: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

# =========================================================
# VALIDAÇÃO
# =========================================================

required_columns = {"setor", "vendas"}

if not required_columns.issubset(df.columns):
    st.error("O CSV precisa conter as colunas: setor e vendas.")
    st.stop()

df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")
df = df.dropna(subset=["setor", "vendas"])

if df.empty:
    st.error("O conjunto de dados está vazio ou contém dados inválidos.")
    st.stop()

# =========================================================
# FILTROS
# =========================================================

st.sidebar.title("Filtros de negócios")

setores = st.sidebar.multiselect(
    "Selecione os setores",
    options=sorted(df["setor"].unique()),
    default=sorted(df["setor"].unique())
)

valor_minimo = int(df["vendas"].min())
valor_maximo = int(df["vendas"].max())

valor_filtro = st.sidebar.slider(
    "Receita mínima",
    valor_minimo,
    valor_maximo,
    valor_minimo
)

df_filtrado = df[
    (df["setor"].isin(setores)) &
    (df["vendas"] >= valor_filtro)
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# =========================================================
# MÉTRICAS
# =========================================================

total_sales = df_filtrado["vendas"].sum()
average_sales = df_filtrado["vendas"].mean()

best_sector = df_filtrado.loc[
    df_filtrado["vendas"].idxmax(),
    "setor"
]

lowest_sector = df_filtrado.loc[
    df_filtrado["vendas"].idxmin(),
    "setor"
]

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Receita total",
    f"R$ {total_sales:,.2f}"
)

col2.metric(
    "Receita média",
    f"R$ {average_sales:,.2f}"
)

col3.metric(
    "Setor superior",
    best_sector
)

col4.metric(
    "Setor mais baixo",
    lowest_sector
)

# =========================================================
# GRÁFICO + RESUMO
# =========================================================

st.divider()

left_col, right_col = st.columns([2, 1])

with left_col:

    st.subheader("Desempenho de vendas por setor")

    chart = px.bar(
        df_filtrado,
        x="setor",
        y="vendas",
        color="setor",
        text_auto=True,
        title="Receita por setor",
        color_discrete_sequence=[
            "#1f4e79",
            "#2f75b5",
            "#548235",
            "#70ad47",
            "#a5a5a5",
            "#264478"
        ],
        labels={
            "setor": "Setor",
            "vendas": "Receita"
        }
    )

    chart.update_traces(
        textposition="outside",
        marker_line_color="#ffffff",
        marker_line_width=1.5
    )

    chart.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="#1f2937"
        ),
        xaxis_title="Setor",
        yaxis_title="Receita",
        title_x=0.01,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(chart, use_container_width=True)

with right_col:

    st.subheader("Sumário executivo")

    st.write(
        f"""
        O setor de melhor desempenho é o de **{best_sector}**,
        representando a maior contribuição para a receita.

        O setor com pior desempenho é o de **{lowest_sector}**,
        o que indica uma oportunidade para revisão comercial e operacional.

        A receita total analisada atingiu **R$ {total_sales:,.2f}**.
        """
    )

# =========================================================
# DATAFRAME
# =========================================================

st.divider()

st.subheader("Conjunto de dados de vendas")

st.dataframe(df_filtrado, use_container_width=True)

# =========================================================
# RECOMENDAÇÕES
# =========================================================

st.divider()

st.subheader("Recomendações de negócios")

st.info(
    f"""
    Próximos passos recomendados:

    1. Investigar os fatores que impulsionam o desempenho do setor de {best_sector}.
    2. Revisar a estratégia comercial do setor de {lowest_sector}.
    3. Expandir os dados com custos, margens, datas e segmentos de clientes.
    4. Aplicar modelos preditivos para projeções futuras.
    """
)

# =========================================================
# OPENAI
# =========================================================

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")

# =========================================================
# ANÁLISE EXECUTIVA
# =========================================================

st.divider()

st.subheader("Análise Executiva de IA")

if not api_key:

    st.warning(
        "OPENAI_API_KEY não encontrada no arquivo .env."
    )

else:

    client = OpenAI(api_key=api_key)

    data_text = df_filtrado.to_string(index=False)

    executive_prompt = f"""
    Você é um consultor executivo especialista em Business Intelligence.

    Analise os dados abaixo e gere:

    1. Resumo executivo
    2. Melhor setor
    3. Pior setor
    4. Insights estratégicos
    5. Recomendações empresariais

    Dados:

    {data_text}
    """

    if st.button("Gerar análise de IA"):

        with st.spinner("Gerando análise executiva..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um consultor executivo especialista em análise de negócios."
                    },
                    {
                        "role": "user",
                        "content": executive_prompt
                    }
                ],
                temperature=0.5
            )

            analysis = response.choices[0].message.content

            st.success("Análise gerada com sucesso.")

            st.markdown(analysis)

# =========================================================
# ASSISTENTE IA
# =========================================================

st.divider()

st.subheader("Assistente de IA")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_question = st.text_area(
    "Faça uma pergunta sobre os dados empresariais:",
    placeholder="Exemplo: Qual setor merece mais investimento?"
)

if st.button("Consultar IA"):

    if not api_key:

        st.warning("Adicione sua chave OPENAI_API_KEY no arquivo .env.")

    elif user_question.strip() == "":

        st.warning("Digite uma pergunta.")

    else:

        client = OpenAI(api_key=api_key)

        business_context = df_filtrado.to_string(index=False)

        assistant_prompt = f"""
        Você é um especialista em Business Intelligence.

        Responda à pergunta do usuário utilizando os dados abaixo.

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
                        "content": "Você é um especialista em análise empresarial."
                    },
                    {
                        "role": "user",
                        "content": assistant_prompt
                    }
                ],
                temperature=0.5
            )

            answer = response.choices[0].message.content

            st.session_state.chat_history.append(
                {
                    "pergunta": user_question,
                    "resposta": answer
                }
            )

            st.success("Resposta gerada com sucesso.")

if st.session_state.chat_history:

    st.subheader("Histórico de conversa")

    for item in reversed(st.session_state.chat_history):

        st.markdown("---")

        st.markdown("**Pergunta**")
        st.write(item["pergunta"])

        st.markdown("**Resposta da IA**")
        st.markdown(item["resposta"])