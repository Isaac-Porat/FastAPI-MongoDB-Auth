import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from contextlib import asynccontextmanager
from models import Token
from motor.motor_asyncio import AsyncIOMotorClient
from auth import register_user, login_user, get_current_user
from admin import create_admin_user, get_current_admin_user
from config import MONGODB_DATABASE_URL, MONGODB_DATABASE_NAME, MONGODB_COLLECTION_NAME
from database import MongoMiddleware

load_dotenv()

logger = logging.getLogger("uvicorn")

app = FastAPI()

app.add_middleware(MongoMiddleware, db_url=MONGODB_DATABASE_URL, db_name=MONGODB_DATABASE_NAME, collection_name=MONGODB_COLLECTION_NAME)

# Initialize development environment
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
    return {"message": "Hello World"}

@app.get("/test-middleware")
async def test_middleware(request: Request):
    if hasattr(request.state, 'collection'):
        return {"message": "Middleware is working"}
    else:
        return {"message": "Middleware is not working"}

@app.get("/create-admin")
async def create_admin(request: Request):
    await create_admin_user(request)

@app.post("/register", response_model=Token)
async def register(user: OAuth2PasswordRequestForm = Depends()) -> Token:
    access_token = await register_user(user)
    return access_token

@app.post("/login", response_model=Token)
async def login(request: Request, user: OAuth2PasswordRequestForm = Depends()) -> Token:
   access_token = await login_user(request, user)
   return access_token

@app.post("/token", response_model=Token)
async def login(request: Request, user: OAuth2PasswordRequestForm = Depends()) -> Token:
   access_token = await login_user(request, user)
   return access_token

@app.get("/users/me")
async def get_current_active_user(request: Request, token: str = Depends(get_current_user)):
    return token

@app.get("/admin/me")
async def get_dashboard(token: str = Depends(get_current_admin_user)):
    return token

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
