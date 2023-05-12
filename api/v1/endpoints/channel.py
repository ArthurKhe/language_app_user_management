from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from schemas.user import User
from settings import settings

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
router = APIRouter()


@router.get("/user/{user_id}/channel/")
async def get_channels(user_id: int):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user:
            user["channels"]
            return JSONResponse({"channels": user["channels"]})
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed"}, status_code=406)
    except PyMongoError as e:
        return JSONResponse({"message": f"Error get channels: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()


@router.post("/user/{user_id}/channel/{channel}")
async def add_channel(user_id: int, channel):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user and channel not in user["channels"]:
            user["channels"].append(channel)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) update channels"})
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed or channel existing"}, status_code=406)
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
            return JSONResponse({"message": f"user ({user_id}) or channel not existed"}, status_code=406)
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete channel: {str(e)}"}, status_code=500)
    except ValueError as e:
        return JSONResponse({"message": f"Error delete channel: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()
