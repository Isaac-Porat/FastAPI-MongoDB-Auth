import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger("uvicorn")

app = FastAPI()

# Initialize auth security
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
logger.warning(f"JWT_SECRET_KEY: {JWT_SECRET_KEY}")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")
logger.warning(f"HASHING_ALGORITHM: {HASHING_ALGORITHM}")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
logger.warning(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=HASHING_ALGORITHM)

    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except jwt.PyJWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)


# Initialize pydantic user model
# class User(BaseModel):
#   username: str
#   password: str

# Initialize MongoDB client and collection
MONGODB_DATABASE_URL = os.getenv("MONGODB_DATABASE_URL")
logger.warning(f"MONGODB_DATABASE_URL: {MONGODB_DATABASE_URL}")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
logger.warning(f"MONGODB_DATABASE_NAME: {MONGODB_DATABASE_NAME}")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
logger.warning(f"MONGODB_COLLECTION_NAME: {MONGODB_COLLECTION_NAME}")
client = AsyncIOMotorClient(MONGODB_DATABASE_URL)
db = client[MONGODB_DATABASE_NAME]
collection = db.get_collection(MONGODB_COLLECTION_NAME)

logger.warning(f"Connected to MongoDB collection: {collection}")

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

@app.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()) -> Token:
    try:
        result = await collection.find_one({"username": user.username})
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": result['inserted_id']})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register", response_model=Token)
async def register(user: OAuth2PasswordRequestForm = Depends()) -> Token:
    try:
        existing_user = await collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await collection.insert_one({"username": user.username, "password": user.password})
        logger.warning(str(result.inserted_id))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User creation failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": str(result.inserted_id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
