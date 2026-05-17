import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqService:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada no arquivo .env")

        self.client = Groq(api_key=api_key)

    def get_client(self):
        return self.client