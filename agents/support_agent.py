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

        total_sales = dataframe[revenue_column].sum()

        average_sales = dataframe[revenue_column].mean()

        best_sector = dataframe.loc[
            dataframe[revenue_column].idxmax()
        ]

        worst_sector = dataframe.loc[
            dataframe[revenue_column].idxmin()
        ]

        business_context = f"""
        Dados empresariais:

        Receita total:
        R$ {total_sales:,.2f}

        Receita média:
        R$ {average_sales:,.2f}

        Melhor setor:
        {best_sector.to_dict()}

        Pior setor:
        {worst_sector.to_dict()}

        Dados completos:
        {dataframe.to_string(index=False)}

        Pergunta:
        {question}
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