from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from schemas.user import User
from settings import settings
from utils.utils import find_dict, update_category, delete_category
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
router = APIRouter()


@router.get("/categories/")
async def get_categories():
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        categories = await mongo_client.language_app.categories.find({}).to_list(length=None)
        result = [{
            "id": str(category["_id"]),
            "name": category["name"]
        }
            for category in categories
        ]
        return result
    finally:
        mongo_client.close()


@router.put("/user/{user_id}/categories/{category_id}")
async def add_category_to_user(user_id: int, category_id):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        categories = await mongo_client.language_app.categories.find({}).to_list(length=None)
        if user and not find_dict(user["categories"], "id", category_id):
            user["categories"] = update_category(categories, user["categories"], category_id)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) update categories"})
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed or category id existing"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()


@router.delete("/user/{user_id}/categories/{category_id}")
async def delete_category_from_user(user_id: int, category_id):
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user and find_dict(user["categories"], "id", category_id):
            user["categories"] = delete_category(user["categories"], category_id)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) delete category"})
        else:
            return JSONResponse({"message": f"user ({user_id}) or category_id not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete category: {str(e)}"}, status_code=500)
    finally:
        mongo_client.close()
