import pandas as pd

from agents.data_validation import prepare_sales_dataframe
from services.openai_service import OpenAIService


class ShopifyAIAgent:
    def __init__(self):
        service = OpenAIService()
        self.client = service.get_client()

    def generate_shopify_insights(self, dataframe: pd.DataFrame):
        insights = []

        try:
            dataframe = prepare_sales_dataframe(dataframe)

            total_revenue = dataframe["vendas"].sum()
            average_revenue = dataframe["vendas"].mean()
            best_segment = dataframe.loc[dataframe["vendas"].idxmax(), "setor"]
            review_segment = dataframe.loc[dataframe["vendas"].idxmin(), "setor"]

            insights.append(f"Receita total analisada: R$ {total_revenue:,.2f}")
            insights.append(f"Receita media por segmento Shopify: R$ {average_revenue:,.2f}")
            insights.append(
                f"Segmento Shopify com maior potencial de crescimento: {best_segment}"
            )
            insights.append(f"Segmento Shopify em revisao operacional: {review_segment}")

            prompt = f"""
            Voce e um especialista em Shopify,
            e-commerce e revenue intelligence.

            Analise os dados abaixo e gere:

            - insights executivos
            - oportunidades de crescimento
            - riscos operacionais
            - recomendacoes estrategicas
            - oportunidades de escala
            - analise de receita

            Dados:

            {dataframe.to_string(index=False)}

            Use somente os dados fornecidos. Nao invente metricas, percentuais, setores ou categorias.
            Responda em portugues profissional.
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        Voce e um consultor executivo
                        especialista em Shopify stores,
                        crescimento de receita,
                        e-commerce e BI empresarial.
                        """,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
            )

            insights.append(response.choices[0].message.content)

            return insights

        except Exception as error:
            return [f"Erro na analise Shopify AI: {str(error)}"]
