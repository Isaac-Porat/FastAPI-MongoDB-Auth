import os
import logging
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from models import Token
from exceptions import UsernameAlreadyExistsException, check_username_exists
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=HASHING_ALGORITHM)

    return encoded_jwt

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        collection = request.state.collection
        user = await collection.find_one({"username": username})
        if user is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    return username

async def register_user(request: Request, user_data: OAuth2PasswordRequestForm) -> Token:
    try:
        # Load in database collection
        collection = request.state.collection

        # Check if the username already exists in the database
        await check_username_exists(collection, user_data.username)

        # Hash the password using a secure hashing algorithm
        hashed_password = get_password_hash(user_data.password)

        # Insert the new user into the database
        result = await collection.insert_one({"username": user_data.username, "password": hashed_password})

        # Generate an access token for the new user
        access_token = create_access_token(data={"sub": str(user_data.username)})

        # Return the access token and token type
        return Token(access_token=access_token, token_type="bearer")

    except UsernameAlreadyExistsException as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    except PyMongoError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

async def login_user(request: Request, user: OAuth2PasswordRequestForm = Depends()) -> Token:
    try:
        # Load in database collection
        collection = request.state.collection

        # Check if the username exists in the database
        result = await collection.find_one({"username": user.username})

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # If the username exists, check to ensure the password and hashed password are the same
        if not pwd_context.verify(user.password, result['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate an access token for the new user
        access_token = create_access_token(data={"sub": str(user.username)})

        # Return the access token and token type
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException as e:
        raise HTTPException(
        status_code=e.status_code,
        detail=str(e.detail)
        )

    except PyMongoError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
        )

