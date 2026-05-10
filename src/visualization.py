# ==========================================
# VISUALIZATION MODULE
# Dashboard Empresarial - Blumenau/SC
# ==========================================

import matplotlib.pyplot as plt


# ==========================================
# GRÁFICO DE LUCRO
# ==========================================

def grafico_lucro(dados):

    plt.figure(figsize=(10, 6))

    plt.bar(
        dados["setor"],
        dados["lucro"]
    )

    plt.title("Lucro por Setor - Blumenau/SC")

    plt.xlabel("Setor")

    plt.ylabel("Lucro (R$)")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()


# ==========================================
# GRÁFICO DE VENDAS
# ==========================================

def grafico_vendas(dados):

    plt.figure(figsize=(10, 6))

    plt.bar(
        dados["setor"],
        dados["vendas"]
    )

    plt.title("Vendas por Setor - Blumenau/SC")

    plt.xlabel("Setor")

    plt.ylabel("Vendas (R$)")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()


# ==========================================
# GRÁFICO DE CUSTOS
# ==========================================

def grafico_custos(dados):

    plt.figure(figsize=(10, 6))

    plt.bar(
        dados["setor"],
        dados["custos"]
    )

    plt.title("Custos por Setor - Blumenau/SC")

    plt.xlabel("Setor")

    plt.ylabel("Custos (R$)")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()


# ==========================================
# DASHBOARD COMPARATIVO
# ==========================================

def dashboard_comparativo(dados):

    plt.figure(figsize=(12, 7))

    plt.plot(
        dados["setor"],
        dados["vendas"],
        marker="o",
        label="Vendas"
    )

    plt.plot(
        dados["setor"],
        dados["custos"],
        marker="o",
        label="Custos"
    )

    plt.plot(
        dados["setor"],
        dados["lucro"],
        marker="o",
        label="Lucro"
    )

    plt.title("Dashboard Empresarial - Blumenau/SC")

    plt.xlabel("Setor")

    plt.ylabel("Valores (R$)")

    plt.xticks(rotation=30)

    plt.legend()

    plt.tight_layout()

    plt.show()