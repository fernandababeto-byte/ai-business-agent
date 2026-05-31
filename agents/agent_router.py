import unicodedata

from agents.executive_agent import ExecutiveAgent
from agents.finance_agent import FinanceAgent
from agents.sales_agent import SalesAgent
from agents.support_agent import SupportAgent


class AgentRouter:
    def __init__(self):
        self.executive_agent = None
        self.sales_agent = None
        self.finance_agent = None
        self.support_agent = None

    def get_executive_agent(self):
        if self.executive_agent is None:
            self.executive_agent = ExecutiveAgent()
        return self.executive_agent

    def get_sales_agent(self):
        if self.sales_agent is None:
            self.sales_agent = SalesAgent()
        return self.sales_agent

    def get_finance_agent(self):
        if self.finance_agent is None:
            self.finance_agent = FinanceAgent()
        return self.finance_agent

    def get_support_agent(self):
        if self.support_agent is None:
            self.support_agent = SupportAgent()
        return self.support_agent

    def route_question(self, question, dataframe):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("A pergunta nao pode estar vazia.")

        question_lower = unicodedata.normalize("NFKD", question.lower())
        question_lower = "".join(
            char for char in question_lower if not unicodedata.combining(char)
        )

        if any(
            word in question_lower
            for word in ["venda", "vendas", "cliente", "comercial", "crescimento"]
        ):
            return self.get_sales_agent().analyze_sales(dataframe)

        if any(
            word in question_lower
            for word in ["lucro", "custo", "margem", "financeiro", "risco"]
        ):
            return self.get_finance_agent().analyze_finance(dataframe)

        if any(
            word in question_lower
            for word in ["resumo", "executivo", "estrategia", "analise"]
        ):
            return self.get_executive_agent().generate_executive_report(dataframe)

        return self.get_support_agent().answer_business_question(question, dataframe)
