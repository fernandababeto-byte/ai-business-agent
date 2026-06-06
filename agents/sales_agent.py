from agents.data_validation import prepare_sales_dataframe
from services.openai_service import OpenAIService


class SalesAgent:
    def __init__(self):
        service = OpenAIService()
        self.client = service.get_client()

    def analyze_sales(self, dataframe):
        dataframe = prepare_sales_dataframe(dataframe)

        total_sales = dataframe["vendas"].sum()

        best_segment = dataframe.loc[
            dataframe["vendas"].idxmax(),
            "setor"
        ]

        prompt = f"""
        Você é um especialista em vendas e crescimento empresarial.

        Analise os dados:

        Receita total: {total_sales}

        Segmento Shopify com maior receita: {best_segment}

        Gere:
        - análise comercial;
        - oportunidades;
        - estratégias;
        - recomendações de crescimento.

        Use somente os dados fornecidos. Nao invente metricas, percentuais, setores ou categorias.
        """

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",

            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor comercial especialista."
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.5
        )

        return response.choices[0].message.content
