from pymongo import MongoClient
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from passlib.context import CryptContext
from main import app
from models import User
from auth import get_password_hash

collection = app.collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user: User):
  try:
    user.hashed_password = get_password_hash(user.password)

    result = collection.insert_one(user.model_dump())

    user_id = result.inserted_id

    return {
      "message": "User created successfully", "id": str(user_id)
    }
  except ValidationError as e:
    raise HTTPException(status_code=400, detail=f"Error inserting user into collection: {e}")

def authenticate_user(username: str, password: str):
    user = collection.find_one({"username": username})
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

