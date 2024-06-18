import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB database URL from environment variables
MONGODB_DATABASE_URL = os.getenv("MONGODB_DATABASE_URL")
# MongoDB database name from environment variables
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
# MongoDB collection name from environment variables
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
# JWT secret key for encoding and decoding JWT tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# Algorithm used for hashing in JWT token creation
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")
# Expiration time in minutes for the access token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
# Admin username from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
# Admin password from environment variables
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")