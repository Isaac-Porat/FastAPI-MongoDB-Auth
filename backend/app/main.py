import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from models import Token
from auth import register_user, login_user, get_current_user
from admin import create_admin_user, get_current_admin_user
from config import MONGODB_DATABASE_URL, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME
from database import MongoMiddleware
from crud import fetch_all_users, delete_user_by_username

load_dotenv()

logger = logging.getLogger("uvicorn")

app = FastAPI()

app.add_middleware(MongoMiddleware, db_url=MONGODB_DATABASE_URL, db_name=MONGODB_DATABASE_NAME, collection_name=MONGODB_COLLECTION_NAME)

environment = "dev"
if environment == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    """
    Root endpoint that returns a simple greeting message.

    Returns:
        dict: A dictionary containing a greeting message.
    """
    return {"message": "Hello World"}

@app.get("/test-middleware")
async def test_middleware(request: Request):
    """
    Endpoint to test if the MongoMiddleware is working.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        dict: A dictionary indicating whether the middleware is working.
    """
    if hasattr(request.state, 'collection'):
        return {"message": "Middleware is working"}
    else:
        return {"message": "Middleware is not working"}

@app.get("/create-admin")
async def create_admin(request: Request):
    """
    Endpoint to create an admin user.

    Args:
        request (Request): The incoming HTTP request.
    """
    await create_admin_user(request)

@app.post("/register", response_model=Token)
async def register(user: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Endpoint to register a new user.

    Args:
        user (OAuth2PasswordRequestForm): The form data for user registration.

    Returns:
        Token: The access token for the registered user.
    """
    access_token = await register_user(user)
    return access_token

@app.post("/login", response_model=Token)
async def login(request: Request, user: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Endpoint to log in a user.

    Args:
        request (Request): The incoming HTTP request.
        user (OAuth2PasswordRequestForm): The form data for user login.

    Returns:
        Token: The access token for the logged-in user.
    """
    access_token = await login_user(request, user)
    return access_token

@app.post("/token", response_model=Token)
async def login(request: Request, user: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Endpoint to obtain a new access token.

    Args:
        request (Request): The incoming HTTP request.
        user (OAuth2PasswordRequestForm): The form data for obtaining a new token.

    Returns:
        Token: The new access token.
    """
    access_token = await login_user(request, user)
    return access_token

@app.get("/users/me")
async def get_current_active_user(request: Request, token: str = Depends(get_current_user)):
    """
    Endpoint to get the current active user.

    Args:
        request (Request): The incoming HTTP request.
        token (str): The token of the current user.

    Returns:
        str: The token of the current user.
    """
    return token

@app.get("/admin/me")
async def get_dashboard(token: str = Depends(get_current_admin_user)):
    """
    Endpoint to get the current admin user.

    Args:
        token (str): The token of the current admin user.

    Returns:
        str: The token of the current admin user.
    """
    return token

@app.get("/admin/users")
async def get_all_users(request: Request, token: str = Depends(get_current_admin_user)):
    """
    Endpoint to fetch all users.

    Args:
        request (Request): The incoming HTTP request.
        token (str): The token of the current admin user.

    Returns:
        list: A list of all users.
    """
    users = await fetch_all_users(request)
    return users

@app.delete("/admin/users/{username}")
async def delete_user(request: Request, username: str, token: str = Depends(get_current_admin_user)):
    """
    Endpoint to delete a user by username.

    Args:
        request (Request): The incoming HTTP request.
        username (str): The username of the user to delete.
        token (str): The token of the current admin user.

    Returns:
        dict: A success message if the user is deleted successfully.
    """
    result = await delete_user_by_username(request, username)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
