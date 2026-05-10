# ==========================================
# ANALYTICS MODULE
# ==========================================

def calcular_metricas(dados):

    total_vendas = dados["vendas"].sum()

    media_vendas = dados["vendas"].mean()

    total_custos = dados["custos"].sum()

    lucro_total = dados["lucro"].sum()

    total_funcionarios = dados["funcionarios"].sum()

    setor_maior_venda = dados.loc[
        dados["vendas"].idxmax(),
        "setor"
    ]

    setor_maior_lucro = dados.loc[
        dados["lucro"].idxmax(),
        "setor"
    ]

    return {
        "total_vendas": total_vendas,
        "media_vendas": media_vendas,
        "total_custos": total_custos,
        "lucro_total": lucro_total,
        "total_funcionarios": total_funcionarios,
        "setor_maior_venda": setor_maior_venda,
        "setor_maior_lucro": setor_maior_lucro
    }


def gerar_diagnostico(lucro_total):

    if lucro_total > 250000:
        return "Empresa com crescimento acelerado"

    elif lucro_total > 150000:
        return "Empresa com crescimento estável"

    else:
        return "Empresa necessita otimização operacional"