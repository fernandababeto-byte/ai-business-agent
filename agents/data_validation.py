import pandas as pd


def prepare_sales_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        raise ValueError("Nenhum dado valido encontrado para analise.")

    df = dataframe.copy()
    df.columns = [str(column).strip().lower() for column in df.columns]

    required_columns = {"setor", "vendas"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dados sem colunas obrigatorias: {missing}")

    df["vendas"] = pd.to_numeric(df["vendas"], errors="coerce")
    df = df.dropna(subset=["setor", "vendas"])

    if df.empty:
        raise ValueError("Nenhuma linha com setor e vendas validos foi encontrada.")

    return df
