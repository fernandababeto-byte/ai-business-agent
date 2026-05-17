import pandas as pd


class AnalystAgent:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None

    def load_data(self):

        try:
            self.data = pd.read_csv(self.file_path)

            print("Dados carregados com sucesso.")
            return self.data

        except Exception as error:

            print(f"Erro ao carregar dados: {error}")
            return None

    def show_data(self):

        if self.data is None:
            print("Nenhum dado carregado.")
            return

        print("\nDataset:")
        print(self.data)

    def show_basic_info(self):

        if self.data is None:
            print("Nenhum dado carregado.")
            return

        print("\nInformações gerais:")
        print(self.data.info())

    def show_statistics(self):

        if self.data is None:
            print("Nenhum dado carregado.")
            return

        print("\nEstatísticas:")
        print(self.data.describe())

    def missing_data_report(self):

        if self.data is None:
            print("Nenhum dado carregado.")
            return

        print("\nValores ausentes:")
        print(self.data.isnull().sum())

    def generate_business_insights(self):

        if self.data is None:
            print("Nenhum dado carregado.")
            return

        total_vendas = self.data["vendas"].sum()

        total_custos = self.data["custos"].sum()

        lucro_total = total_vendas - total_custos

        melhor_setor = self.data.loc[
            self.data["vendas"].idxmax()
        ]["setor"]

        print("\nInsights de negócio:")

        print(f"Total de vendas: {total_vendas}")

        print(f"Total de custos: {total_custos}")

        print(f"Lucro total estimado: {lucro_total}")

        print(f"Setor com maior venda: {melhor_setor}")

    def run(self):

        self.load_data()

        self.show_data()

        self.show_basic_info()

        self.show_statistics()

        self.missing_data_report()

        self.generate_business_insights()


if __name__ == "__main__":

    agent = AnalystAgent("data/vendas_blumenau.csv")

    agent.run()