from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    chat_id: int
    categories: List
    channels: List