"""Run from the repository root: python -m examples.revenue_demo."""
from decimal import Decimal

from services.revenue_scenario import revenue_with_one_order


def main():
    # Synthetic BRL amounts, newest first. No customer or store data.
    orders = [Decimal(v) for v in ("300.00", "200.00", "100.00", "1000.00")]
    revenue = sum(orders, Decimal("0"))
    scenario = revenue_with_one_order(orders)
    extra_order = scenario - revenue
    print("DEMONSTRAÇÃO — DADOS FICTÍCIOS — SEM CONEXÃO COM SHOPIFY")
    print(f"Pedidos de exemplo (mais recente primeiro): {orders}")
    print(f"Receita dos 4 pedidos: BRL {revenue:.2f}")
    print(f"Média dos 3 pedidos mais recentes: BRL {extra_order:.2f}")
    print(f"Cenário com um pedido hipotético adicional: BRL {scenario:.2f}")
    print("Hipótese: um pedido adicional igual à média recente.")
    print("Não é previsão por IA, receita futura garantida ou crescimento mensal.")


if __name__ == "__main__":
    main()
