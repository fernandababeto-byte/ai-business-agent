import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_html(markup: str) -> None:
    st.markdown(markup.strip(), unsafe_allow_html=True)


def render_forecast_section(
    average_revenue,
    best_category,
    risk_category,
    format_currency,
):
    render_html(
        '<div class="ai-card">'
        '<div class="ai-badge">SHOPIFY FORECAST ENGINE</div>'
        '<div class="ai-title">Previsão Inteligente de Receita</div>'
        '<div class="ai-subtitle">'
        'Inteligência preditiva para crescimento, expansão comercial, '
        'tendências de receita e oportunidades Shopify.'
        '</div>'
        '</div>'
    )

    forecast_values = []
    base_value = float(average_revenue) if average_revenue else 0

    for month_index in range(1, 7):
        projected_growth = base_value * (1 + (0.08 * month_index))
        forecast_values.append(projected_growth)

    forecast_df = pd.DataFrame(
        {
            "Período": ["Mês 1", "Mês 2", "Mês 3", "Mês 4", "Mês 5", "Mês 6"],
            "Receita Prevista": forecast_values,
        }
    )

    forecast_fig = go.Figure()

    forecast_fig.add_trace(
        go.Scatter(
            x=forecast_df["Período"],
            y=forecast_df["Receita Prevista"],
            mode="lines+markers",
            line=dict(color="#60A5FA", width=5, shape="spline"),
            marker=dict(
                size=11,
                color="#FFFFFF",
                line=dict(color="#2563EB", width=3),
            ),
            fill="tozeroy",
            fillcolor="rgba(37,99,235,0.16)",
            hovertemplate="<b>%{x}</b><br>Receita Prevista: R$ %{y:,.2f}<extra></extra>",
            name="Forecast IA",
        )
    )

    forecast_fig.add_trace(
        go.Scatter(
            x=forecast_df["Período"],
            y=forecast_df["Receita Prevista"],
            mode="lines",
            line=dict(
                color="rgba(96,165,250,0.18)",
                width=16,
                shape="spline",
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    forecast_fig.update_layout(
        height=360,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        hoverlabel=dict(
            bgcolor="#111827",
            bordercolor="#2563EB",
            font_size=14,
            font_color="white",
        ),
        font=dict(color="#FFFFFF", size=14, family="Arial"),
        xaxis=dict(
            showgrid=False,
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#CBD5E1", size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
            tickfont=dict(color="#CBD5E1", size=12),
        ),
    )

    st.plotly_chart(forecast_fig, use_container_width=True)

    if forecast_values and forecast_values[0] > 0:
        forecast_growth = (
            (forecast_values[-1] - forecast_values[0]) / forecast_values[0]
        ) * 100
    else:
        forecast_growth = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Crescimento Projetado",
            f"{forecast_growth:.1f}%",
            "Próximos 6 ciclos",
        )

    with col2:
        st.metric(
            "Receita Potencial",
            format_currency(forecast_values[-1] if forecast_values else 0),
            "Estimativa futura",
        )

    with col3:
        st.metric(
            "Categoria para Escala",
            best_category,
            "Maior potencial atual",
        )

    render_html(
        f'<div class="ai-response-box">'
        f'<b>Análise Preditiva Shopify:</b><br><br>'
        f'• Tendência geral de crescimento positivo para os próximos ciclos.<br><br>'
        f'• A categoria <b>{best_category}</b> apresenta o maior potencial de escala comercial.<br><br>'
        f'• A categoria <b>{risk_category}</b> deve ser revisada para evitar perda de performance.<br><br>'
        f'• A receita potencial projetada é de '
        f'<b>{format_currency(forecast_values[-1] if forecast_values else 0)}</b>.<br><br>'
        f'• A recomendação estratégica é aumentar investimento nas categorias com maior resposta de receita '
        f'e revisar categorias com desempenho inferior.'
        f'</div>'
    )

    return forecast_growth
