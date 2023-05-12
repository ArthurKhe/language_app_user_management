from fastapi import APIRouter
from fastapi.responses import JSONResponse

from settings import settings
from utils.utils import find_dict, update_category, delete_category
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from db.repository import MongoRepository
from utils.exceptions import UserNotExistingException, CategoryExistingException, CategoryNotExistedException
router = APIRouter()


@router.get("/categories/")
async def get_categories():
    try:
        repository = MongoRepository(settings.MONGO_URL)
        categories = await repository.get_categories()
        return categories
    except Exception as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=500)
    finally:
        repository.client.close()


@router.put("/user/{user_id}/categories/{category_id}")
async def add_category_to_user(user_id: int, category_id):
    try:
        repository = MongoRepository(settings.MONGO_URL)
        updated_user = await repository.add_category_to_user(user_id, category_id)
        return updated_user
    except CategoryExistingException as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=400)
    except UserNotExistingException as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=400)
    except PyMongoError as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=500)
    finally:
        repository.client.close()


@router.delete("/user/{user_id}/categories/{category_id}")
async def delete_category_from_user(user_id: int, category_id):
    try:
        repository = MongoRepository(settings.MONGO_URL)
        updated_user = await repository.delete_category_from_user(user_id, category_id)
        return updated_user
    except CategoryNotExistedException as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=400)
    except UserNotExistingException as e:
        return JSONResponse({"message": f"Error update user: {str(e)}"}, status_code=400)
    except PyMongoError as e:
        return JSONResponse({"message": f"Error delete category: {str(e)}"}, status_code=500)
    finally:
        repository.client.close()
