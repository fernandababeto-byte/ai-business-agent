import html
import streamlit as st


def _build_alerts(
    growth_rate,
    best_category,
    risk_category,
    total_revenue,
):
    alerts = []

    if growth_rate >= 20:
        alerts.append(
            {
                "status": "SUCCESS",
                "label": "AI SUCCESS",
                "title": "Crescimento antecipado detectado",
                "description": f"A operação apresentou crescimento de {growth_rate:.1f}%.",
                "time": "Updated now",
            }
        )

    if total_revenue >= 500000:
        alerts.append(
            {
                "status": "ENTERPRISE",
                "label": "ENTERPRISE",
                "title": "Receita corporativa identificada",
                "description": f"Receita consolidada acima de R$ {total_revenue:,.0f}.",
                "time": "Updated now",
            }
        )

    alerts.append(
        {
            "status": "PRIORITY",
            "label": "PRIORITY",
            "title": "Categoria estratégica",
            "description": f"{best_category} apresenta alto potencial de expansão.",
            "time": "Updated now",
        }
    )

    alerts.append(
        {
            "status": "RISK",
            "label": "RISK",
            "title": "Risco operacional detectado",
            "description": f"{risk_category} necessita atenção executiva.",
            "time": "Updated now",
        }
    )

    return alerts


def render_alerts_section(
    growth_rate,
    best_category,
    risk_category,
    total_revenue,
):
    st.divider()

    st.markdown(
        '<div class="ai-card">'
        '<div class="ai-badge">EXECUTIVE AI MONITORING</div>'
        '<div class="ai-title">Centro de Monitoramento de IA</div>'
        '<div class="ai-subtitle">'
        'Sistema exclusivo de monitoramento executivo, riscos operacionais, crescimento e oportunidades.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    alerts = _build_alerts(
        growth_rate=growth_rate,
        best_category=best_category,
        risk_category=risk_category,
        total_revenue=total_revenue,
    )

    for alert in alerts:
        status = html.escape(str(alert["status"]).lower())
        label = html.escape(str(alert["label"]))
        title = html.escape(str(alert["title"]))
        description = html.escape(str(alert["description"]))
        time_label = html.escape(str(alert["time"]))

        st.markdown(
            f'<div class="enterprise-alert-card">'
            f'<div class="enterprise-alert-top">'
            f'<div class="enterprise-alert-status {status}">{label}</div>'
            f'<div class="enterprise-alert-time" '
            f'style="color:#64748B;font-size:10px;font-weight:800;letter-spacing:0.6px;text-transform:uppercase;">'
            f'{time_label}</div>'
            f'</div>'
            f'<div class="enterprise-alert-title">{title}</div>'
            f'<div class="enterprise-alert-description">{description}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
