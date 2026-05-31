import streamlit as st


def _format_currency(value):
    """Formata valores numéricos para exibição monetária."""
    try:
        return f"R$ {float(value):,.0f}"
    except Exception:
        return "R$ 0"


def _format_percent(value):
    """Formata valores percentuais para exibição."""
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "0.0%"


def _render_html(html: str) -> None:
    """Renderiza HTML sem indentação para evitar que o Streamlit mostre código cru."""
    st.markdown(html.strip(), unsafe_allow_html=True)


def render_kpi_section(
    total_revenue,
    avg_ticket,
    forecast_value,
    growth_rate,
):
    """Renderiza a seção premium de KPIs executivos."""

    _render_html(
        """
<style>
.section-title-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92));
    border: 1px solid rgba(147,197,253,0.14);
    border-radius: 22px;
    padding: 18px 20px;
    margin-top: 12px;
    margin-bottom: 16px;
    box-shadow:
        0 18px 46px rgba(0,0,0,0.32),
        0 0 26px rgba(37,99,235,0.08);
}
.section-badge {
    display: inline-block;
    background: rgba(37,99,235,0.18);
    color: #93C5FD !important;
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
    border: 1px solid rgba(147,197,253,0.24);
}
.section-title {
    color: #FFFFFF !important;
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
}
.section-subtitle {
    color: #CBD5E1 !important;
    font-size: 13px;
    line-height: 1.45;
}
.executive-kpi-card {
    min-height: 104px;
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 36%),
        linear-gradient(145deg, rgba(15,23,42,0.98), rgba(30,41,59,0.94));
    border: 1px solid rgba(147,197,253,0.16);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow:
        0 14px 38px rgba(0,0,0,0.32),
        0 0 24px rgba(37,99,235,0.08);
}
.executive-kpi-label {
    color: #93C5FD !important;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.executive-kpi-value {
    color: #FFFFFF !important;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: -0.4px;
}
</style>
"""
    )

    _render_html(
        '<div class="section-title-card">'
        '<div class="section-badge">EXECUTIVE KPI ENGINE</div>'
        '<div class="section-title">Revenue Intelligence KPIs</div>'
        '<div class="section-subtitle">Monitoramento executivo de receita, crescimento, forecast e performance operacional Shopify.</div>'
        '</div>'
    )

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("RECEITA TOTAL", _format_currency(total_revenue)),
        ("TICKET MÉDIO", _format_currency(avg_ticket)),
        ("FORECAST", _format_currency(forecast_value)),
        ("CRESCIMENTO", _format_percent(growth_rate)),
    ]

    for column, (label, value) in zip([col1, col2, col3, col4], cards):
        with column:
            _render_html(
                f'<div class="executive-kpi-card">'
                f'<div class="executive-kpi-label">{label}</div>'
                f'<div class="executive-kpi-value">{value}</div>'
                f'</div>'
            )
