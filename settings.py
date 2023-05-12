import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MONGO_URL = os.getenv("MONGO_URL", default="mongodb://root:example@127.0.0.1:27017")
    API_V1_STR: str = "/api/v1"


settings = Settings()
