import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Business Agent",
    page_icon="",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #0f172a;
    }
    .section-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Business Agent Dashboard")

st.markdown(
    """
    Professional business intelligence dashboard for sales monitoring, sector performance analysis
    and automated executive insights.
    """
)

df = pd.read_csv("../data/vendas.csv")

total_sales = df["vendas"].sum()
average_sales = df["vendas"].mean()
highest_sale = df["vendas"].max()
lowest_sale = df["vendas"].min()

best_sector = df.loc[df["vendas"].idxmax(), "setor"]
lowest_sector = df.loc[df["vendas"].idxmin(), "setor"]

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"R$ {total_sales:,.2f}")
col2.metric("Average Revenue", f"R$ {average_sales:,.2f}")
col3.metric("Top Sector", best_sector)
col4.metric("Lowest Sector", lowest_sector)

st.divider()

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Sales Performance by Sector")

    chart = px.bar(
        df,
        x="setor",
        y="vendas",
        color="setor",
        text_auto=True,
        labels={
            "setor": "Sector",
            "vendas": "Revenue"
        }
    )

    chart.update_layout(
        showlegend=False,
        xaxis_title="Sector",
        yaxis_title="Revenue",
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(chart, use_container_width=True)

with right_col:
    st.subheader("Executive Summary")

    st.write(
        f"""
        The highest-performing sector is **{best_sector}**, with the strongest revenue contribution.

        The lowest-performing sector is **{lowest_sector}**, indicating an opportunity for operational review.

        Total analyzed revenue reached **R$ {total_sales:,.2f}**.
        """
    )

st.divider()

st.subheader("Sales Dataset")

st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("Business Recommendations")

st.info(
    f"""
    Recommended next steps:

    1. Investigate the performance drivers behind the {best_sector} sector.
    2. Review commercial strategy for the {lowest_sector} sector.
    3. Expand the dataset with costs, profit margins, dates and client segments.
    4. Apply predictive models to estimate future revenue.
    """
)