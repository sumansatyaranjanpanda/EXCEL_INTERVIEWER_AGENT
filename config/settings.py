import os
from dotenv import load_dotenv

load_dotenv()  # load .env file at startup

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"  # optional
