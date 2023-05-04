import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", default="mongodb://localhost:27017/language_app")
