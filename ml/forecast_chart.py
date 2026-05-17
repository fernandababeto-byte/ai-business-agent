import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


class ForecastChart:

    def create_chart(self, dataframe: pd.DataFrame):
        df = dataframe.copy()
        df = df.reset_index(drop=True)
        df["periodo"] = df.index + 1

        x = df[["periodo"]]
        y = df["vendas"]

        model = LinearRegression()
        model.fit(x, y)

        next_period = len(df) + 1
        prediction = model.predict([[next_period]])[0]

        forecast_df = pd.DataFrame(
            {
                "periodo": list(df["periodo"]) + [next_period],
                "vendas": list(df["vendas"]) + [prediction],
                "tipo": ["Real"] * len(df) + ["Previsão IA"],
            }
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=forecast_df["periodo"],
                y=forecast_df["vendas"],
                mode="lines+markers",
                name="Vendas e previsão",
            )
        )

        fig.update_layout(
            title="Tendência de vendas com previsão IA",
            xaxis_title="Período",
            yaxis_title="Vendas",
            plot_bgcolor="#F8FAFC",
            paper_bgcolor="#F8FAFC",
        )

        return fig