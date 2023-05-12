from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from typing import List

from schemas.user import User
from utils.utils import find_dict, update_category, delete_category
from utils.exceptions import UserNotExistingException, CategoryExistingException, CategoryNotExistedException


class MongoRepository:
    def __init__(self, mongo_url: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client["language_app"]
        self.user_collection = self.db["users"]
        self.category_collection = self.db["categories"]

    async def create_user(self, user: User) -> User:
        existing_user = await self.user_collection.find_one({"user_id": user.user_id})
        if existing_user:
            # Пользователь уже существует
            return None
        else:
            # Пользователя нет в коллекции
            result = await self.user_collection.insert_one(user.dict())
            created_user = await self.user_collection.find_one({"_id": ObjectId(result.inserted_id)})
            return User(**created_user)

    async def get_user(self, user_id: int) -> User:
        user_data = await self.user_collection.find_one({"user_id": user_id})
        if user_data:
            return User(**user_data)
        else:
            return None

    async def update_user(self, user_id: int, fields: dict) -> User:
        await self.user_collection.update_one({"user_id": user_id}, {"$set": fields})
        updated_user = await self.user_collection.find_one({"user_id": user_id})
        return User(**updated_user)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.user_collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def get_users(self) -> List[User]:
        users_data = await self.user_collection.find().to_list(length=None)
        users = [User(**user_data) for user_data in users_data]
        return users

    async def get_categories(self):
        categories = await self.category_collection.find({}).to_list(length=None)
        result = [{
            "id": str(category["_id"]),
            "name": category["name"]
            }
            for category in categories
        ]
        return result

    async def add_category_to_user(self, user_id: int, category_id):
        user = await self.user_collection.find_one({"user_id": user_id})
        categories = await self.category_collection.find({}).to_list(length=None)
        if not find_dict(user["categories"], "id", category_id):
            raise CategoryExistingException("Category already exists")
        if user:
            user["categories"] = update_category(categories, user["categories"], category_id)
            await self.user_collection.replace_one({"_id": user["_id"]}, user)
            return user
        else:
            raise UserNotExistingException("User does not exist")

    async def delete_category_from_user(self, user_id: int, category_id):
        user = await self.user_collection.find_one({"user_id": user_id})
        if not find_dict(user["categories"], "id", category_id):
            raise CategoryNotExistedException("Category does not exist")
        if user and find_dict(user["categories"], "id", category_id):
            user["categories"] = delete_category(user["categories"], category_id)
            await self.user_collection.replace_one({"_id": user["_id"]}, user)
            return user
        else:
            raise UserNotExistingException("User does not exist")

