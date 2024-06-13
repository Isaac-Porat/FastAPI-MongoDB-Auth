import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pymongo import MongoClient
from contextlib import asynccontextmanager
from config import MONGODB_COLLECTION_NAME, MONGODB_DATABASE_NAME, MONGODB_DATABASE_URL
from models import User
from auth import login_for_access_token, register_for_access_token

app = FastAPI()

@asynccontextmanager
async def lifetime(app: FastAPI):
    app.client = MongoClient(MONGODB_DATABASE_URL)

    app.db = app.client[MONGODB_DATABASE_NAME]

    app.collection = app.db[MONGODB_COLLECTION_NAME]

    yield

    app.client.close()

environment = "dev"

if environment == "dev":
    logger = logging.getLogger("uvicorn")
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

@app.post("/register")
async def register(user: User):
    register_for_access_token(user)

@app.post("/login")
async def login(user: User):
    login_for_access_token(user)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
