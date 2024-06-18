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
    """
    Hashes a password using the configured password hashing context.

    Args:
    password (str): The password to hash.

    Returns:
    str: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """
    Creates a JWT access token.

    Args:
    data (dict): The data to encode in the token.

    Returns:
    str: The encoded JWT token.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=HASHING_ALGORITHM)

    return encoded_jwt

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user based on the provided JWT token.

    Args:
    request (Request): The request object that includes the database collection.
    token (str): The JWT token.

    Returns:
    str: The username of the current user.

    Raises:
    HTTPException: If the token is invalid or the user does not exist.
    """
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
    """
    Registers a new user in the database.

    Args:
    request (Request): The request object that includes the database collection.
    user_data (OAuth2PasswordRequestForm): The user data from the registration form.

    Returns:
    Token: The access token and token type for the new user.

    Raises:
    HTTPException: If the username already exists, there is a database error, or an unexpected error occurs.
    """
    try:
        collection = request.state.collection

        await check_username_exists(collection, user_data.username)

        hashed_password = get_password_hash(user_data.password)

        result = await collection.insert_one({"username": user_data.username, "password": hashed_password})

        access_token = create_access_token(data={"sub": str(user_data.username)})

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
    """
    Logs in a user by verifying their credentials and generating an access token.

    Args:
    request (Request): The request object that includes the database collection.
    user (OAuth2PasswordRequestForm): The user data from the login form.

    Returns:
    Token: The access token and token type for the logged-in user.

    Raises:
    HTTPException: If the username or password is incorrect, there is a database error, or an unexpected error occurs.
    """
    try:
        collection = request.state.collection

        result = await collection.find_one({"username": user.username})

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not pwd_context.verify(user.password, result['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": str(user.username)})

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

