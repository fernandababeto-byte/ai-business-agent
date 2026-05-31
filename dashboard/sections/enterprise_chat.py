import html
import pandas as pd
import requests
import streamlit as st


def render_html(markup: str) -> None:
    st.markdown(markup.strip(), unsafe_allow_html=True)


def render_enterprise_chat(
    total_sales,
    average_sales,
    best_sector,
    lowest_sector,
    next_prediction,
    premium_dataframe,
    safe_text,
    API_CONSULT_URL,
    API_HISTORY_URL,
):
    st.divider()

    render_html(
        '<div class="ai-card">'
        '<div class="ai-badge">ENTERPRISE AI COPILOT</div>'
        '<div class="ai-title">Chat Empresarial IA Premium</div>'
        '<div class="ai-subtitle">'
        'Copiloto executivo para analisar receita, categorias, riscos, '
        'oportunidades de escala, forecast e decisões comerciais.'
        '</div>'
        '</div>'
    )

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    history_count = 0

    try:
        response = requests.get(API_HISTORY_URL, timeout=20)
        result = response.json()
        api_history = result.get("history", [])
        history_count = len(api_history)
    except Exception:
        api_history = []

    render_html(
        f'<div class="enterprise-chat-shell">'
        f'<div class="enterprise-chat-header">'
        f'<div>'
        f'<div class="enterprise-chat-badge">● AI COPILOT ONLINE</div>'
        f'<div class="enterprise-chat-title">Copiloto de Receita Empresarial</div>'
        f'<div class="enterprise-chat-subtitle">'
        f'Converse com a IA sobre crescimento, vendas, desempenho, riscos operacionais e oportunidades Shopify.'
        f'</div>'
        f'</div>'
        f'<div class="copilot-status-grid">'
        f'<div class="copilot-mini-card">'
        f'<div class="copilot-mini-label">Mensagens</div>'
        f'<div class="copilot-mini-value">{len(st.session_state.chat_messages)}</div>'
        f'</div>'
        f'<div class="copilot-mini-card">'
        f'<div class="copilot-mini-label">Históricos</div>'
        f'<div class="copilot-mini-value">{history_count}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    if not st.session_state.chat_messages:
        render_html(
            '<div class="enterprise-chat-empty">'
            '<b>Comece uma análise executiva.</b><br>'
            'Faça uma pergunta como: “Quais categorias devo priorizar para aumentar receita?” '
            'ou “Onde existe maior risco operacional?”.'
            '</div>'
        )

    for message in st.session_state.chat_messages[-8:]:
        role = message.get("role", "assistant")
        content = html.escape(str(message.get("content", ""))).replace("\n", "<br>")

        if role == "user":
            render_html(
                f'<div class="enterprise-message-row user">'
                f'<div class="enterprise-message user">'
                f'<div class="enterprise-message-meta">'
                f'<span class="enterprise-avatar">U</span> VOCÊ'
                f'</div>'
                f'{content}'
                f'</div>'
                f'</div>'
            )
        else:
            render_html(
                f'<div class="enterprise-message-row assistant">'
                f'<div class="enterprise-message assistant">'
                f'<div class="enterprise-message-meta">'
                f'<span class="enterprise-avatar">IA</span> SHOPIFY AI COPILOT'
                f'</div>'
                f'{content}'
                f'</div>'
                f'</div>'
            )

    render_html(
        '<div class="enterprise-chat-input-card">'
        '<div class="enterprise-chat-badge">CENTRO DE ATENDIMENTO EXECUTIVO</div>'
        '<div class="enterprise-quick-prompts">'
        '<span class="enterprise-prompt-pill">Priorizar categorias</span>'
        '<span class="enterprise-prompt-pill">Encontrar riscos</span>'
        '<span class="enterprise-prompt-pill">Aumentar receita</span>'
        '<span class="enterprise-prompt-pill">Melhorar forecast</span>'
        '</div>'
        '</div>'
    )

    user_question = st.text_input(
        "Digite sua pergunta empresarial",
        placeholder="Consulte sobre receita, previsão, risco operacional ou crescimento Shopify...",
        key="enterprise_chat_question",
    )

    send_col1, send_col2 = st.columns([1, 3])

    with send_col1:
        send_question = st.button("Enviar para IA")

    with send_col2:
        clear_chat = st.button("Limpar conversa")

    if clear_chat:
        st.session_state.chat_messages = []
        st.rerun()

    if send_question:
        if not user_question.strip():
            st.warning("Digite uma pergunta antes de enviar.")
        else:
            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            try:
                with st.spinner("Analisando dados empresariais com IA..."):
                    response = requests.post(
                        API_CONSULT_URL,
                        json={
                            "question": user_question,
                            "context": {
                                "total_revenue": float(total_sales),
                                "average_revenue": float(average_sales),
                                "best_category": str(best_sector),
                                "risk_category": str(lowest_sector),
                                "forecast": float(next_prediction),
                            },
                        },
                        timeout=120,
                    )

                    result = response.json()

                    if "error" in result:
                        answer = result["error"]
                    else:
                        answer = result.get("response", "Sem resposta.")

                    answer = safe_text(answer)

            except requests.exceptions.ConnectionError:
                answer = (
                    "API indisponível. Execute no terminal: docker compose up --build."
                )

            except Exception as error:
                answer = f"Erro ao consultar a IA: {error}"

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            st.rerun()

    st.divider()

    render_html(
        '<div class="chat-card">'
        '<div class="ai-badge">MEMÓRIA DE CONVERSAÇÃO</div>'
        '<div class="chat-title">Histórico de Conversas</div>'
        '<div class="chat-subtitle">'
        'Registro das consultas realizadas pelo copiloto empresarial.'
        '</div>'
        '</div>'
    )

    try:
        response = requests.get(API_HISTORY_URL, timeout=30)
        result = response.json()
        history = result.get("history", [])

        if history:
            history_df = pd.DataFrame(history)

            history_df = history_df.rename(
                columns={
                    "created_at": "Data",
                    "question": "Pergunta",
                    "answer": "Resposta",
                }
            )

            premium_dataframe(history_df)

        else:
            render_html(
                '<div class="enterprise-history-card">Nenhum histórico encontrado.</div>'
            )

    except requests.exceptions.ConnectionError:
        st.error("Não foi possível carregar o histórico. API indisponível.")

    except Exception as error:
        st.error(f"Erro ao carregar histórico: {error}")
