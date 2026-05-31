import pandas as pd
from sklearn.linear_model import LinearRegression


class SalesForecast:

    def predict_next_value(self, dataframe: pd.DataFrame):
        df = dataframe.copy()
        if df.empty or "vendas" not in df.columns:
            raise ValueError("Dados insuficientes para gerar previsao.")

        df = df.reset_index()
        df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")
        df = df.dropna(subset=["vendas"])
        if df.empty:
            raise ValueError("Nenhuma venda valida encontrada para gerar previsao.")

        df["periodo"] = df.index + 1

        x = df[["periodo"]]
        y = df["vendas"]

        model = LinearRegression()
        model.fit(x, y)

        next_period = pd.DataFrame({"periodo": [len(df) + 1]})
        prediction = model.predict(next_period)[0]

        return round(float(prediction), 2)
