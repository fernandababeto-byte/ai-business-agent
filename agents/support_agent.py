import pandas as pd

from services.groq_service import GroqService


class SupportAgent:

    def __init__(self):
        groq_service = GroqService()
        self.client = groq_service.get_client()

    def answer_business_question(
        self,
        question,
        dataframe: pd.DataFrame
    ):
        if dataframe is None or dataframe.empty:
            return "Nenhum dado valido encontrado para analise."

        dataframe = dataframe.copy()
        dataframe.columns = [
            col.lower().strip()
            for col in dataframe.columns
        ]

        revenue_column = None

        possible_columns = [
            "receita",
            "faturamento",
            "valor",
            "vendas"
        ]

        for col in possible_columns:
            if col in dataframe.columns:
                revenue_column = col
                break

        if revenue_column is None:
            return f"""
            Nenhuma coluna de receita encontrada.

            Colunas disponíveis:
            {list(dataframe.columns)}
            """

        dataframe[revenue_column] = pd.to_numeric(
            dataframe[revenue_column],
            errors="coerce"
        )
        dataframe = dataframe.dropna(subset=[revenue_column])
        if dataframe.empty:
            return "Nenhuma linha com receita valida foi encontrada."

        total_sales = dataframe[revenue_column].sum()

        average_sales = dataframe[revenue_column].mean()

        best_segment = dataframe.loc[
            dataframe[revenue_column].idxmax()
        ]

        review_segment = dataframe.loc[
            dataframe[revenue_column].idxmin()
        ]

        business_context = f"""
        Dados empresariais:

        Receita total:
        R$ {total_sales:,.2f}

        Receita média:
        R$ {average_sales:,.2f}

        Segmento Shopify com maior receita:
        {best_segment.to_dict()}

        Segmento Shopify em revisao operacional:
        {review_segment.to_dict()}

        Dados completos:
        {dataframe.to_string(index=False)}

        Pergunta:
        {question}

        Use somente os dados fornecidos. Nao invente metricas, percentuais, setores ou categorias.
        """

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Você é um consultor empresarial executivo.
                    Gere análises estratégicas,
                    profissionais,
                    detalhadas
                    e corporativas.
                    """
                },
                {
                    "role": "user",
                    "content": business_context
                }
            ],
            temperature=0.5,
            max_tokens=1200
        )

        return response.choices[0].message.content
