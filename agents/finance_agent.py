from agents.data_validation import prepare_sales_dataframe
from services.openai_service import OpenAIService


class FinanceAgent:
    def __init__(self):
        service = OpenAIService()
        self.client = service.get_client()

    def analyze_finance(self, dataframe):
        dataframe = prepare_sales_dataframe(dataframe)

        total_sales = dataframe["vendas"].sum()

        prompt = f"""
        Você é um diretor financeiro empresarial.

        Analise os dados:

        Receita total: {total_sales}

        Custos, lucro e margem: indisponiveis. Estes dados ainda nao foram
        sincronizados pela integracao Shopify.

        Nao invente custos, lucro, margem, ROAS, CAC, LTV ou churn.
        Explique claramente quando uma metrica depende de uma nova fonte de dados.

        Gere:

        - análise financeira;
        - riscos;
        - eficiência operacional;
        - redução de custos;
        - estratégias financeiras;
        - recomendações executivas.
        """

        response = self.client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[

                {
                    "role": "system",
                    "content": "Você é um CFO especialista."
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4
        )

        return response.choices[0].message.content
