# Demonstração sem loja Shopify

Esta demonstração funciona localmente com dados fictícios. Não exige conta Shopify, credenciais, banco de dados, pagamentos ou chamadas a serviços de IA. Não conecta o dashboard principal a uma loja e não grava snapshots.

## Executar

Na raiz do repositório, usando Python 3.10 ou superior:

```bash
python -m examples.revenue_demo
```

O exemplo usa apenas a biblioteca padrão do Python e o mesmo cálculo utilizado pelo serviço de sincronização.

## Resultado esperado

| Informação | Valor em BRL |
| --- | ---: |
| Pedidos fictícios, do mais recente ao mais antigo | 300, 200, 100, 1.000 |
| Receita observada no exemplo | 1.600,00 |
| Média dos três pedidos mais recentes | 200,00 |
| Receita com um pedido hipotético adicional | 1.800,00 |

O valor de 1.800,00 é um cenário aritmético. Não há previsão temporal, modelo de IA ou promessa de crescimento.

## Verificação automatizada

Com as dependências de teste disponíveis, execute na raiz:

```bash
python -m unittest discover -s tests -v
```

Os testes simulam as respostas da Shopify, persistência e notificações. Verificam paginação, loja vazia ou desconectada, falha de consulta sem tentativa de salvar dados parciais e repetição da sincronização sem acumular o pedido hipotético.

## Estado da validação

A demonstração e os testes permitem desenvolver sem possuir loja real. A integração externa permanece não validada: OAuth, permissões efetivas, respostas reais da API, gravação em banco e operação do dashboard completo ainda precisam de um ambiente de integração apropriado antes de oferecer conexão Shopify a usuários.

Não é necessário criar uma loja real para executar este exemplo. Os dados fictícios devem permanecer identificados como demonstração e separados de dados de clientes.
