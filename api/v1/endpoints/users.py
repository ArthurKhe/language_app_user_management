from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from schemas.user import User
from settings import settings

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
router = APIRouter()


@router.get("/user/")
async def get_users():
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    try:
        users = await mongo_client.language_app.users.find({}).to_list(length=None)
        mongo_client.close()
        if users:
            return [User(**user) for user in users]
        else:
            return JSONResponse({"message": f"users not existed"}, status_code=404)
    finally:
        mongo_client.close()


@router.get("/user/{user_id}")
async def get_user(user_id: int):
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    try:
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        mongo_client.close()
        if user:
            return User(**user)
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed"}, status_code=404)
    finally:
        mongo_client.close()


@router.post("/user/")
async def create_user(user_id: int, chat_id: int):
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    user = {
        "user_id": user_id,
        "chat_id": chat_id,
        "categories": [],
        "channels": []
    }
    try:
        existing_user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if existing_user:
            # Пользователь уже существует
            return JSONResponse({"message": f"user ({user_id}) existing"})
        else:
            # Пользователя нет в коллекции
            await mongo_client.language_app.users.insert_one(user)
            return Response(content=User(**user).json(), status_code=201, media_type="application/json")
    except PyMongoError as e:
        return JSONResponse({"message": f"Error inserting user: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()
