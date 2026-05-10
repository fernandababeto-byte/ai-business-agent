# ==========================================
# AI BUSINESS AGENT API
# Blumenau/SC
# ==========================================

from fastapi import FastAPI
import pandas as pd

from src.analytics import (
    calcular_metricas,
    gerar_diagnostico
)

from src.machine_learning import (
    treinar_modelo,
    prever_vendas
)


# ==========================================
# INICIALIZAÇÃO DA API
# ==========================================

app = FastAPI()


# ==========================================
# LEITURA DOS DADOS
# ==========================================

dados = pd.read_csv("./data/vendas_blumenau.csv")
dados["lucro"] = dados["vendas"] - dados["custos"]


# ==========================================
# ENDPOINT PRINCIPAL
# ==========================================

@app.get("/")
def home():
    metricas = calcular_metricas(dados)

    diagnostico = gerar_diagnostico(
        metricas["lucro_total"]
    )

    return {
        "projeto": "AI Business Agent",
        "cidade": "Blumenau/SC",
        "diagnostico": diagnostico,
        "lucro_total": float(metricas["lucro_total"]),
        "total_vendas": float(metricas["total_vendas"]),
        "total_custos": float(metricas["total_custos"]),
        "total_funcionarios": int(metricas["total_funcionarios"]),
        "setor_maior_lucro": str(metricas["setor_maior_lucro"])
    }


# ==========================================
# ENDPOINT DE MACHINE LEARNING
# ==========================================

@app.get("/previsao/{funcionarios}")
def previsao(funcionarios: int):
    modelo = treinar_modelo(dados)

    resultado = prever_vendas(
        modelo,
        funcionarios
    )

    return {
        "funcionarios": int(funcionarios),
        "previsao_vendas": float(round(resultado, 2))
    }