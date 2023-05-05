from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from settings import settings
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.errors import PyMongoError
from typing import List, Dict, Any
from pydantic import BaseModel
app = FastAPI()
mongo_client = AsyncIOMotorClient("mongodb://root:example@127.0.0.1:27017")


class User(BaseModel):
    user_id: int
    chat_id: int
    categories: List
    channels: List


def find_dict(my_list, key, value):
    """
    Ищет словарь в списке my_list, который содержит значение value для ключа key.
    """
    for d in my_list:
        if str(d.get(key)) == value:
            return d
    return None


def update_category(categories, user_categories, category_id):
    user_categories.append({
        "id": category_id,
        "name": find_dict(categories, "_id", category_id)["name"]
    })
    return user_categories


def delete_category(user_categories, category_id):
    for d in user_categories:
        if str(d.get("id")) == category_id:
            user_categories.remove(d)
            break
    return user_categories


@app.post("/user/")
async def create_user(user_id: int, chat_id: int):
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


@app.get("/user/{user_id}")
async def get_user(user_id: int):
    user = await mongo_client.language_app.users.find_one({"user_id": user_id})
    if user:
        return User(**user)
    else:
        return JSONResponse({"message": f"user ({user_id}) not existed"}, status_code=404)


@app.get("/categories/")
async def get_categories() -> List[Dict[str, Any]]:
    categories = await mongo_client.language_app.categories.find({}).to_list(length=None)
    result = [{
        "id": str(category["_id"]),
        "name": category["name"]
    }
        for category in categories
    ]
    return result


@app.put("/user/{user_id}/categories/{category_id}")
async def add_category_to_user(user_id: int, category_id):
    try:
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


@app.delete("/user/{user_id}/categories/{category_id}")
async def delete_category_from_user(user_id: int, category_id):
    try:
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user and find_dict(user["categories"], "id", category_id):
            user["categories"] = delete_category(user["categories"], category_id)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) delete category"})
        else:
            return JSONResponse({"message": f"user ({user_id}) or category_id not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete category: {str(e)}"}, status_code=500)


@app.post("/user/{user_id}/channel/{channel}")
async def add_channel(user_id: int, channel):
    try:
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user:
            user["channels"].append(channel)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) update channels"})
        else:
            return JSONResponse({"message": f"user ({user_id}) not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error add channel: {str(e)}"}, status_code=500)


@app.delete("/user/{user_id}/channel/{channel}")
async def delete_channel(user_id: int, channel):
    try:
        user = await mongo_client.language_app.users.find_one({"user_id": user_id})
        if user and channel in user["channels"]:
            user["channels"].remove(channel)
            await mongo_client.language_app.users.replace_one({"_id": user["_id"]}, user)
            return JSONResponse({"message": f"user ({user_id}) delete channel"})
        else:
            return JSONResponse({"message": f"user ({user_id}) or channel not existed"})
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete channel: {str(e)}"}, status_code=500)
