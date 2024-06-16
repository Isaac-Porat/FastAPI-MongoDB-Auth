import os
import logging
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from auth import get_current_user
from fastapi import Depends, HTTPException, status

logger = logging.getLogger("uvicorn")

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def create_admin_user(collection: Collection):
    try:
        logger.info("Attempting to find existing admin user.")
        existing_admin = collection.find_one({"username": ADMIN_USERNAME})

        if existing_admin:
            logger.info("Admin user already exists.")
        else:
            logger.info("Admin user not found. Creating a new admin user.")
            admin_user = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "is_admin": True
            }
            collection.insert_one(admin_user)
            logger.info("Admin user created successfully.")
    except PyMongoError as e:
        logger.error(f"Database error while creating admin user: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while creating admin user: {e}", exc_info=True)

async def get_current_admin_user(token: str = Depends(get_current_user)):
  logger.warning(token)
  if token != ADMIN_USERNAME:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Unauthorized access attempt by non-admin user",
          headers={"WWW-Authenticate": "Bearer"},
      )
  return {"status_code": 200, "message": "Admin user authenticated successfully"}
