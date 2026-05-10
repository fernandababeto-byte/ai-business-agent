# ==========================================
# MACHINE LEARNING MODULE
# ==========================================

from sklearn.linear_model import LinearRegression


def treinar_modelo(dados):

    X = dados[["funcionarios"]]

    y = dados["vendas"]

    modelo = LinearRegression()

    modelo.fit(X, y)

    return modelo


def prever_vendas(modelo, funcionarios):

    previsao = modelo.predict([[funcionarios]])

    return previsao[0]