from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class FinanceAgent:

    def analyze_finance(self, dataframe):

        total_sales = dataframe["vendas"].sum()

        estimated_cost = total_sales * 0.65

        estimated_profit = total_sales - estimated_cost

        profit_margin = (
            estimated_profit / total_sales
        ) * 100

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

        response = client.chat.completions.create(

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