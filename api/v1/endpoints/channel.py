from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from schemas.user import User
from settings import settings

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
router = APIRouter()


@router.post("/user/{user_id}/channel/{channel}")
async def add_channel(user_id: int, channel):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user:
            user["channels"].append(channel)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) update channels"})
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error add channel: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()


@router.delete("/user/{user_id}/channel/{channel}")
async def delete_channel(user_id: int, channel):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user and channel in user["channels"]:
            user["channels"].remove(channel)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) delete channel"})
        else:
            return JSONResponse({"message": f"user ({user_id}) or channel not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete channel: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()
