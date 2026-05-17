from agents.executive_agent import ExecutiveAgent
from agents.sales_agent import SalesAgent
from agents.finance_agent import FinanceAgent
from agents.support_agent import SupportAgent


class AgentRouter:

    def __init__(self):
        self.executive_agent = ExecutiveAgent()
        self.sales_agent = SalesAgent()
        self.finance_agent = FinanceAgent()
        self.support_agent = SupportAgent()

    def route(self, question, dataframe):
        question_lower = question.lower()

        if any(word in question_lower for word in ["venda", "cliente", "comercial", "crescimento"]):
            return self.sales_agent.analyze_sales(dataframe)

        if any(word in question_lower for word in ["lucro", "custo", "margem", "financeiro", "risco"]):
            return self.finance_agent.analyze_finance(dataframe)

        if any(word in question_lower for word in ["resumo", "executivo", "estratégia", "estrategia"]):
            return self.executive_agent.generate_executive_report(dataframe)

        return self.support_agent.answer_business_question(
            question,
            dataframe
        )