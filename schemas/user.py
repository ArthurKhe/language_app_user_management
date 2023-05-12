from pydantic import BaseModel
from typing import List
from schemas.category import Category


class User(BaseModel):
    user_id: int
    chat_id: int
    categories: List
    channels: List
