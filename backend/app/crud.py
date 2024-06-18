import os
import logging
from fastapi import HTTPException, status, Request
from bson import ObjectId
from pymongo.errors import PyMongoError

logger = logging.getLogger("uvicorn")

def convert_objectid_to_str(item):
    """
    Recursively converts ObjectId instances in a data structure to their string representation.

    Args:
    item (Any): The item to convert, which can be an ObjectId, a dictionary, a list, or any other type.

    Returns:
    Any: The converted item with ObjectId instances replaced by their string representation.
    """
    if isinstance(item, ObjectId):
        return str(item)
    elif isinstance(item, dict):
        return {key: convert_objectid_to_str(value) for key, value in item.items()}
    elif isinstance(item, list):
        return [convert_objectid_to_str(element) for element in item]
    return item

async def fetch_all_users(request: Request):
    """
    Fetches all users from the database and converts their ObjectId fields to strings.

    Args:
    request (Request): The request object that includes the database collection.

    Returns:
    list: A list of users with ObjectId fields converted to strings.

    Raises:
    HTTPException: If there is a database error or an unexpected error occurs.
    """
    try:
        collection = request.state.collection
        users = await collection.find().to_list(None)
        converted_users = [convert_objectid_to_str(user) for user in users]
        return converted_users

    except PyMongoError as e:
        logger.error(f"Failed to fetch users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users from database"
        )

    except Exception as e:
        logger.error(f"Failed to fetch users: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users from database"
        )

async def delete_user_by_username(request: Request, username: str):
    """
    Deletes a user from the database by their username.

    Args:
    request (Request): The request object that includes the database collection.
    username (str): The username of the user to delete.

    Returns:
    dict: A success message if the user is deleted successfully.

    Raises:
    HTTPException: If the user is not found, there is a database error, or an unexpected error occurs.
    """
    try:
        collection = request.state.collection
        delete_result = await collection.delete_one({"username": username})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"status": "success", "message": "User deleted successfully."}

    except PyMongoError as e:
        logger.error(f"Database error during user deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during user deletion"
        )

    except Exception as e:
        logger.error(f"Unexpected error during user deletion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user deletion"
        )
