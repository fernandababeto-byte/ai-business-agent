# ==========================================
# AI BUSINESS AGENT
# Sistema Empresarial Inteligente
# Blumenau/SC
# ==========================================

import pandas as pd

from src.analytics import (
    calcular_metricas,
    gerar_diagnostico
)

from src.visualization import (
    grafico_lucro,
    grafico_vendas,
    grafico_custos,
    dashboard_comparativo
)

from src.machine_learning import (
    treinar_modelo,
    prever_vendas
)

from visualization import (
    grafico_lucro,
    grafico_vendas,
    grafico_custos,
    dashboard_comparativo
)

from machine_learning import (
    treinar_modelo,
    prever_vendas
)


# ==========================================
# LEITURA DOS DADOS
# ==========================================

dados = pd.read_csv("data/vendas_blumenau.csv")


# ==========================================
# PROCESSAMENTO
# ==========================================

dados["lucro"] = dados["vendas"] - dados["custos"]


# ==========================================
# ANALYTICS
# ==========================================

metricas = calcular_metricas(dados)

diagnostico = gerar_diagnostico(
    metricas["lucro_total"]
)


# ==========================================
# MACHINE LEARNING
# ==========================================

modelo = treinar_modelo(dados)

previsao = prever_vendas(
    modelo,
    50
)


# ==========================================
# RELATÓRIO EXECUTIVO
# ==========================================

print("\n===== AI BUSINESS AGENT =====")

print("\n===== RELATÓRIO EXECUTIVO =====")

print(
    f"Total de vendas: "
    f"R$ {metricas['total_vendas']:,.2f}"
)

print(
    f"Lucro total: "
    f"R$ {metricas['lucro_total']:,.2f}"
)

print(
    f"Setor com maior lucro: "
    f"{metricas['setor_maior_lucro']}"
)

print(
    f"Diagnóstico empresarial: "
    f"{diagnostico}"
)

print(
    f"Previsão de vendas para "
    f"empresa com 50 funcionários: "
    f"R$ {previsao:,.2f}"
)

print("==========================================")


# ==========================================
# VISUALIZAÇÃO
# ==========================================

grafico_vendas(dados)

grafico_custos(dados)

grafico_lucro(dados)

dashboard_comparativo(dados)