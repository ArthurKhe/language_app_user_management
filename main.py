from fastapi import FastAPI
from fastapi.responses import JSONResponse
from settings import MONGO_URL
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.errors import PyMongoError

app = FastAPI()
mongo_client = AsyncIOMotorClient("mongodb://root:example@127.0.0.1:27017")


@app.post("/user/")
async def create_user(user_id: int, chat_id: int):
    user = {
        "user_id": user_id,
        "chat_id": chat_id,
        "categories": [],
        "channels": []
    }
    try:
        await mongo_client.language_app.users.insert_one(user)
        return JSONResponse({"message": f"user ({user_id}) created"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error inserting user: {str(e)}"}, status_code=500)
