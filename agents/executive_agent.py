from agents.data_validation import prepare_sales_dataframe
from services.groq_service import GroqService


class ExecutiveAgent:
    def __init__(self):
        service = GroqService()
        self.client = service.get_client()

    def generate_executive_report(self, dataframe):
        dataframe = prepare_sales_dataframe(dataframe)

        total_sales = dataframe["vendas"].sum()
        average_sales = dataframe["vendas"].mean()

        best_segment = dataframe.loc[
            dataframe["vendas"].idxmax(),
            "setor"
        ]

        review_segment = dataframe.loc[
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

Segmento Shopify com maior receita:
{best_segment}

Segmento Shopify em revisao operacional:
{review_segment}

Tabela de receita por segmento Shopify:
{table_data}

Estrutura obrigatória:

1. Resumo Executivo
Explique o cenário geral da empresa.

2. Segmento com Maior Receita
Explique por que esse segmento Shopify se destaca.

3. Segmento em Revisao Operacional
Explique possíveis causas do baixo desempenho.

4. Insights Estratégicos
Liste insights estratégicos claros e completos.

5. Recomendações Empresariais
Crie recomendações práticas e detalhadas.

Use português profissional.
Use somente os dados fornecidos. Nao invente metricas, percentuais, setores ou categorias.
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
