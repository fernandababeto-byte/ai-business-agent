"""Legacy reference component; no temporal forecast is available here."""

import math

import streamlit as st


def render_forecast_section(
    average_revenue,
    best_category,
    risk_category,
    format_currency,
):
    st.subheader("Referência de receita")
    st.caption(
        "Média fornecida pelos dados analisados. Não representa receita mensal, "
        "previsão por IA ou crescimento esperado."
    )
    try:
        reference = float(average_revenue)
    except (TypeError, ValueError):
        reference = None
    if reference is None or not math.isfinite(reference):
        st.info("Referência indisponível: não há uma média válida.")
        return None

    st.metric("Média de referência", format_currency(reference))
    st.write("Categoria com maior receita observada:", str(best_category))
    st.write("Categoria com menor receita observada:", str(risk_category))
    st.info(
        "Previsão indisponível. É necessário um histórico temporal adequado "
        "e validar o modelo antes de apresentar estimativas futuras."
    )
    return None
