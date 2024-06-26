import os
import logging
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from auth import get_current_user
from fastapi import Depends, HTTPException, status, Request
from auth import get_password_hash

logger = logging.getLogger("uvicorn")

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

async def create_admin_user(request: Request):
    """
    Asynchronously creates an admin user in the database if one does not already exist.

    Args:
    request (Request): The request object that includes the database collection.

    Returns:
    tuple: A success message with status code 201 if the admin user is created successfully.

    Raises:
    HTTPException: If an admin user already exists or if there is a database error.
    """
    try:
        collection = request.state.collection

        existing_admin = await collection.find_one({"username": ADMIN_USERNAME})

        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Admin user already exists.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        else:
            admin_user = {
                "username": ADMIN_USERNAME,
                "password": get_password_hash(ADMIN_PASSWORD),
                "is_admin": True
            }
            await collection.insert_one(admin_user)
            return {"status": "success", "message": "Admin user created successfully."}, 201

    except PyMongoError as e:
        logger.error(f"Database error while creating admin user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating admin user.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while creating admin user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while creating admin user.",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_admin_user(request: Request, token: str = Depends(get_current_user)):
    """
    Retrieves the current admin user based on the provided token.

    Args:
    request (Request): The request object that includes the database collection.
    token (str): The token that identifies the user.

    Returns:
    str: The username of the admin user if the token is valid and the user is an admin.

    Raises:
    HTTPException: If the user is not an admin or if the token does not correspond to a valid user.
    """
    collection = request.state.collection

    username = token
    logger.warning(f"Username: {username}")

    result = await collection.find_one({"username": username})

    if result['username'] != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access attempt by non-admin user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username
