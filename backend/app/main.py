import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from models import Token
from auth import register_user, login_user

load_dotenv()

logger = logging.getLogger("uvicorn")

# Initialize MongoDB client and collection
MONGODB_DATABASE_URL = os.getenv("MONGODB_DATABASE_URL")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.client = AsyncIOMotorClient(MONGODB_DATABASE_URL)

    app.db = app.client[MONGODB_DATABASE_NAME]

    app.collection = app.db.get_collection(MONGODB_COLLECTION_NAME)

    logger.warning(f"Connected to MongoDB collection: {app.collection}")

    yield

    await app.client.close()

app = FastAPI(lifespan=lifespan)

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

@app.post("/register", response_model=Token)
async def register(user: OAuth2PasswordRequestForm = Depends()) -> Token:
    access_token = await register_user(app.collection, user)
    return access_token

@app.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()) -> Token:
   access_token = await login_user(app.collection, user)
   return access_token

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
