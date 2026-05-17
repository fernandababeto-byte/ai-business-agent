import pandas as pd
from sklearn.linear_model import LinearRegression


class SalesForecast:

    def predict_next_value(self, dataframe: pd.DataFrame):
        df = dataframe.copy()

        df = df.reset_index()
        df["periodo"] = df.index + 1

        x = df[["periodo"]]
        y = df["vendas"]

        model = LinearRegression()
        model.fit(x, y)

        next_period = [[len(df) + 1]]
        prediction = model.predict(next_period)[0]

        return round(float(prediction), 2)