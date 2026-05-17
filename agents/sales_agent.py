from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class SalesAgent:

    def analyze_sales(self, dataframe):

        total_sales = dataframe["vendas"].sum()

        best_sector = dataframe.loc[
            dataframe["vendas"].idxmax(),
            "setor"
        ]

        prompt = f"""
        Você é um especialista em vendas e crescimento empresarial.

        Analise os dados:

        Receita total: {total_sales}

        Melhor setor: {best_sector}

        Gere:
        - análise comercial;
        - oportunidades;
        - estratégias;
        - recomendações de crescimento.
        """

        response = client.chat.completions.create(
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