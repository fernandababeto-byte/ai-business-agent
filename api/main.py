import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from agents.support_agent import SupportAgent


app = FastAPI(
    title="AI Business Agent API"
)


class BusinessQuestion(BaseModel):
    question: str


DATA_PATH = BASE_DIR / "data" / "vendas.csv"
MEMORY_PATH = BASE_DIR / "memory" / "api_history.csv"


@app.get("/")
def home():
    return {
        "status": "online",
        "platform": "AI Business Agent"
    }


@app.post("/consult")
def consult(data: BusinessQuestion):
    try:
        if not DATA_PATH.exists():
            return {
                "error": "Arquivo vendas.csv não encontrado."
            }

        dataframe = pd.read_csv(DATA_PATH)

        support_agent = SupportAgent()

        response = support_agent.answer_business_question(
            data.question,
            dataframe
        )

        MEMORY_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        new_row = pd.DataFrame(
            [
                {
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "origem": "api",
                    "pergunta": data.question,
                    "resposta": response,
                }
            ]
        )

        if MEMORY_PATH.exists():
            history_df = pd.read_csv(MEMORY_PATH)
            history_df = pd.concat(
                [history_df, new_row],
                ignore_index=True
            )
        else:
            history_df = new_row

        history_df.to_csv(
            MEMORY_PATH,
            index=False
        )

        return {
            "question": data.question,
            "response": response
        }

    except Exception as error:
        return {
            "error": str(error)
        }


@app.get("/history")
def history():
    try:
        if not MEMORY_PATH.exists():
            return {
                "history": []
            }

        history_df = pd.read_csv(MEMORY_PATH)

        return {
            "history": history_df.tail(20).to_dict(orient="records")
        }

    except Exception as error:
        return {
            "error": str(error)
        }