import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit_authenticator as stauth

from agents.executive_agent import ExecutiveAgent
from agents.finance_agent import FinanceAgent
from agents.sales_agent import SalesAgent
from ml.sales_forecast import SalesForecast
from ml.forecast_chart import ForecastChart
from services.pdf_service import PDFService


st.set_page_config(page_title="AI Business Agent", layout="wide")

PRIMARY_BLUE = "#16324F"
SECONDARY_BLUE = "#1F4E79"
CORPORATE_GREEN = "#2E7D32"
LIGHT_BACKGROUND = "#F5F7FA"
SIDEBAR_BACKGROUND = "#EEF3F0"
TEXT_COLOR = "#1F2937"

API_URL = "http://127.0.0.1:8000/consult"

CHART_COLORS = [
    "#16324F",
    "#1F4E79",
    "#2F75B5",
    "#548235",
    "#70AD47",
]

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {LIGHT_BACKGROUND}; }}
    .block-container {{ padding-top: 2rem; max-width: 1500px; }}
    h1 {{ color: {PRIMARY_BLUE}; font-weight: 700; }}
    h2, h3 {{ color: {TEXT_COLOR}; }}
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BACKGROUND}; }}

    .stMetric {{
        background-color: white;
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid {CORPORATE_GREEN};
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}

    .stButton button {{
        background-color: {SECONDARY_BLUE};
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        min-width: 180px;
    }}

    .stButton button:hover {{
        background-color: {PRIMARY_BLUE};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding-top:10px;">
            <h1 style="font-size:28px;">Negócios de IA</h1>
            <p>Plataforma de Análise Empresarial</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


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
    "auth_key",
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
    st.error("Usuário ou senha incorretos.")
    st.stop()

if authentication_status is None:
    st.info("Digite login e senha.")
    st.stop()

authenticator.logout("Sair", "sidebar")
st.sidebar.success(f"Bem-vinda, {name}")


st.title("Painel de controle do agente de negócios com IA")

st.markdown(
    """
    Plataforma corporativa com Business Intelligence,
    Machine Learning e Inteligência Artificial.
    """
)


DATA_PATH = BASE_DIR / "data" / "vendas.csv"
MEMORY_PATH = BASE_DIR / "memory" / "chat_history.csv"
REPORT_PATH = BASE_DIR / "reports" / "relatorio_executivo.pdf"


st.divider()
st.subheader("Fonte de dados")

uploaded_file = st.file_uploader(
    "Faça upload de um arquivo CSV ou Excel",
    type=["csv", "xlsx"],
)

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Formato não suportado. Envie CSV ou Excel (.xlsx).")
        st.stop()
else:
    if not DATA_PATH.exists():
        st.error(f"Arquivo não encontrado: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)


df.columns = [
    str(column).strip().lower()
    for column in df.columns
]

required_columns = {"setor", "vendas"}

if not required_columns.issubset(df.columns):
    st.error("O arquivo precisa conter as colunas: setor e vendas")
    st.stop()

df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")
df = df.dropna(subset=["setor", "vendas"])

if df.empty:
    st.error("Dataset vazio ou inválido.")
    st.stop()


st.sidebar.markdown("## Filtros estratégicos")

selected_sectors = st.sidebar.multiselect(
    "Selecione os setores",
    options=sorted(df["setor"].unique()),
    default=sorted(df["setor"].unique()),
)

min_revenue = int(df["vendas"].min())
max_revenue = int(df["vendas"].max())

selected_min_revenue = st.sidebar.slider(
    "Receita mínima",
    min_revenue,
    max_revenue,
    min_revenue,
)

filtered_df = df[
    (df["setor"].isin(selected_sectors))
    & (df["vendas"] >= selected_min_revenue)
]

if filtered_df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()


total_sales = filtered_df["vendas"].sum()
average_sales = filtered_df["vendas"].mean()

best_sector = filtered_df.loc[
    filtered_df["vendas"].idxmax(),
    "setor"
]

lowest_sector = filtered_df.loc[
    filtered_df["vendas"].idxmin(),
    "setor"
]

forecast_model = SalesForecast()
next_prediction = forecast_model.predict_next_value(filtered_df)

forecast_chart_model = ForecastChart()
forecast_chart = forecast_chart_model.create_chart(filtered_df)


st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Receita Total", f"R$ {total_sales:,.2f}")
col2.metric("Receita Média", f"R$ {average_sales:,.2f}")
col3.metric("Melhor Setor", best_sector)
col4.metric("Setor Crítico", lowest_sector)
col5.metric("Previsão IA", f"R$ {next_prediction:,.2f}")


st.divider()

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Desempenho de vendas por setor")

    chart = px.bar(
        filtered_df,
        x="setor",
        y="vendas",
        color="setor",
        text_auto=True,
        color_discrete_sequence=CHART_COLORS,
    )

    chart.update_layout(
        showlegend=False,
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="#F8FAFC",
    )

    st.plotly_chart(chart, use_container_width=True)

    st.subheader("Previsão inteligente de vendas")
    st.plotly_chart(forecast_chart, use_container_width=True)

with right_col:
    st.subheader("Sumário")

    st.write(
        f"""
        O setor de melhor desempenho é **{best_sector}**.

        O setor com menor desempenho é **{lowest_sector}**.

        Receita total analisada:
        **R$ {total_sales:,.2f}**

        Próxima previsão:
        **R$ {next_prediction:,.2f}**
        """
    )


st.divider()
st.subheader("Conjunto de dados")

st.dataframe(
    filtered_df,
    use_container_width=True
)


st.divider()
st.subheader("Recomendações estratégicas")

st.info(
    f"""
    • Investir no setor de {best_sector}

    • Revisar problemas do setor {lowest_sector}

    • Expandir modelos preditivos

    • Melhorar margem operacional

    • Continuar crescimento baseado em IA
    """
)


st.divider()
st.subheader("Análise executiva IA")

if st.button("Gerar análise executiva"):
    try:
        with st.spinner("Executando IA..."):
            executive_agent = ExecutiveAgent()
            report = executive_agent.generate_executive_report(filtered_df)

        st.success("Relatório gerado.")
        st.write(report)

        pdf_service = PDFService()

        pdf_path = pdf_service.generate_pdf(
            str(report),
            str(REPORT_PATH)
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Baixar relatório em PDF",
                data=pdf_file,
                file_name="relatorio_executivo.pdf",
                mime="application/pdf",
            )

    except Exception as error:
        st.error(f"Erro: {error}")


st.divider()
st.subheader("Chat empresarial IA")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_question = st.text_input(
    "Digite sua pergunta empresarial",
    placeholder="Exemplo: Faça um resumo executivo"
)

if st.button("Enviar pergunta para IA"):
    if not user_question.strip():
        st.warning("Digite uma pergunta antes de enviar.")
    else:
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": user_question,
            }
        )

        with st.chat_message("user"):
            st.write(user_question)

        try:
            with st.spinner("Consultando IA..."):
                response = requests.post(
                    API_URL,
                    json={"question": user_question},
                    timeout=90,
                )

                result = response.json()

                if "error" in result:
                    answer = result["error"]
                else:
                    answer = result.get("response", "Sem resposta.")

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            with st.chat_message("assistant"):
                st.write(answer)

            MEMORY_PATH.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            new_row = pd.DataFrame(
                [
                    {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "pergunta": user_question,
                        "resposta": answer,
                    }
                ]
            )

            if MEMORY_PATH.exists():
                history_df = pd.read_csv(MEMORY_PATH)
                history_df = pd.concat(
                    [history_df, new_row],
                    ignore_index=True
                )
            else:
                history_df = new_row

            history_df.to_csv(
                MEMORY_PATH,
                index=False
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "API não está rodando. Execute em outro terminal: uvicorn api.main:app --reload"
            )

        except Exception as error:
            st.error(f"Erro: {error}")


st.divider()
st.subheader("Agente comercial")

if st.button("Executar análise comercial"):
    try:
        with st.spinner("Executando SalesAgent..."):
            sales_agent = SalesAgent()
            sales_report = sales_agent.analyze_sales(filtered_df)

        st.success("Análise concluída.")
        st.write(sales_report)

    except Exception as error:
        st.error(f"Erro: {error}")


st.divider()
st.subheader("Agente financeiro")

if st.button("Executar análise financeira"):
    try:
        with st.spinner("Executando FinanceAgent..."):
            finance_agent = FinanceAgent()
            finance_report = finance_agent.analyze_finance(filtered_df)

        st.success("Análise concluída.")
        st.write(finance_report)

    except Exception as error:
        st.error(f"Erro: {error}")


st.divider()
st.subheader("Histórico de conversas")

try:
    if MEMORY_PATH.exists():
        history_df = pd.read_csv(MEMORY_PATH)
        st.dataframe(
            history_df.tail(10),
            use_container_width=True
        )
    else:
        st.info("Nenhum histórico encontrado.")

except Exception as error:
    st.error(f"Erro: {error}")