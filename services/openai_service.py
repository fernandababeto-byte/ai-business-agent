import os

from pathlib import Path

from dotenv import load_dotenv

from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class OpenAIService:

    def __init__(self):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:

            raise ValueError(
                "OPENAI_API_KEY nao encontrada no arquivo .env"
            )

        self.client = OpenAI(
            api_key=api_key
        )

    def get_client(self):

        return self.client