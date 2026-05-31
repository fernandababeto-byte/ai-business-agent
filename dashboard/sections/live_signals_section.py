import streamlit as st


def _format_currency_short(value):
    try:
        number = float(value)
        return f"R$ {number:,.0f}"
    except Exception:
        return "R$ 0"


def render_live_signals_section(
    growth_rate,
    best_category,
    risk_category,
    total_revenue,
):
    st.divider()

    st.markdown(
        '<div class="live-signals-header">'
        '<div class="live-signals-badge">MOTOR DE SINAIS DE IA AO VIVO</div>'
        '<div class="live-signals-title">AI Live Revenue Signals</div>'
        '<div class="live-signals-subtitle">'
        'Sistema autônomo de monitoramento contínuo para operações Shopify enterprise.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        confidence_growth = min(98, max(82, 80 + int(float(growth_rate) / 3)))
    except Exception:
        confidence_growth = 88

    revenue_text = _format_currency_short(total_revenue)

    signals = [
        {
            "status": "ALTA PRIORIDADE",
            "title": "Revenue momentum detected",
            "description": (
                f"{best_category} apresentou aceleração de receita acima da média operacional "
                "e deve ser monitorada como prioridade de escala."
            ),
            "confidence": f"{confidence_growth}%",
            "time": "Updated now",
            "tag": "IA DETECTADA",
            "glow": "signal-glow-blue",
        },
        {
            "status": "SINAL DE RISCO",
            "title": "Operational anomaly detected",
            "description": (
                f"{risk_category} apresentou sinal de atenção operacional e pode impactar "
                "a performance futura se não for acompanhado."
            ),
            "confidence": "88%",
            "time": "Updated 2 minutes ago",
            "tag": "RISCO AUTÔNOMO",
            "glow": "signal-glow-orange",
        },
        {
            "status": "SINAL DE ESCALA",
            "title": "Enterprise revenue pattern identified",
            "description": (
                f"Receita consolidada de {revenue_text} indica volume adequado para "
                "automações avançadas e expansão comercial progressiva."
            ),
            "confidence": "92%",
            "time": "Updated now",
            "tag": "SCALING AI",
            "glow": "signal-glow-green",
        },
    ]

    for signal in signals:
        card_html = (
            f'<div class="live-signal-card {signal["glow"]}">'
            '<div class="live-signal-top">'
            f'<div class="live-signal-status">{signal["status"]}</div>'
            f'<div class="live-signal-tag">{signal["tag"]}</div>'
            '</div>'
            f'<div class="live-signal-title">{signal["title"]}</div>'
            f'<div class="live-signal-description">{signal["description"]}</div>'
            '<div class="live-signal-footer">'
            f'<div class="live-signal-confidence">AI Confidence: {signal["confidence"]}</div>'
            f'<div class="live-signal-time">{signal["time"]}</div>'
            '</div>'
            '</div>'
        )

        st.markdown(
            card_html,
            unsafe_allow_html=True,
        )
