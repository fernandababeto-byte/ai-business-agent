from services.groq_service import GroqService


class ExecutiveAgent:
    def __init__(self):
        service = GroqService()
        self.client = service.get_client()

    def generate_executive_report(self, dataframe):
        total_sales = dataframe["vendas"].sum()
        average_sales = dataframe["vendas"].mean()

        best_sector = dataframe.loc[
            dataframe["vendas"].idxmax(),
            "setor"
        ]

        worst_sector = dataframe.loc[
            dataframe["vendas"].idxmin(),
            "setor"
        ]

        table_data = dataframe.to_string(index=False)

        prompt = f"""
Você é um consultor executivo sênior especializado em estratégia empresarial.

Crie um relatório executivo profissional, completo e detalhado.

Não corte frases.
Não deixe pensamentos incompletos.
Não finalize tópicos no meio.
Escreva frases completas.

Dados analisados:

Receita total:
R$ {total_sales:,.2f}

Receita média:
R$ {average_sales:,.2f}

Melhor setor:
{best_sector}

Pior setor:
{worst_sector}

Tabela de vendas:
{table_data}

Estrutura obrigatória:

1. Resumo Executivo
Explique o cenário geral da empresa.

2. Melhor Setor
Explique por que o setor de melhor desempenho se destaca.

3. Pior Setor
Explique possíveis causas do baixo desempenho.

4. Insights Estratégicos
Liste insights estratégicos claros e completos.

5. Recomendações Empresariais
Crie recomendações práticas e detalhadas.

Use português profissional.
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor executivo especialista em análise empresarial."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=2500
        )

        return response.choices[0].message.content