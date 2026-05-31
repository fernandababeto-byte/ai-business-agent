from agents.data_validation import prepare_sales_dataframe
from services.openai_service import OpenAIService


class FinanceAgent:
    def __init__(self):
        service = OpenAIService()
        self.client = service.get_client()

    def analyze_finance(self, dataframe):
        dataframe = prepare_sales_dataframe(dataframe)

        total_sales = dataframe["vendas"].sum()

        estimated_cost = total_sales * 0.65

        estimated_profit = total_sales - estimated_cost

        if total_sales > 0:
            profit_margin = (estimated_profit / total_sales) * 100
        else:
            profit_margin = 0

        prompt = f"""
        Você é um diretor financeiro empresarial.

        Analise os dados:

        Receita total: {total_sales}

        Custo estimado: {estimated_cost}

        Lucro estimado: {estimated_profit}

        Margem estimada: {profit_margin:.2f}%

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
