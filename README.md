# FastAPI Application Overview

## Description
This FastAPI application provides a backend service with several endpoints for user management, authentication, and administrative tasks. It integrates MongoDB for data storage and utilizes middleware for various functionalities.

## Key Features
- **User Authentication**: Register and login endpoints that handle user authentication and token generation.
- **Admin Operations**: Endpoints for admin users to manage regular users and perform administrative tasks.
- **Middleware Integration**: Includes middleware for MongoDB connection handling and CORS settings for development mode.

## Environment Variables
To run this application, you need to set up the following environment variables in your `.env` file:
- `MONGODB_DATABASE_URL`: URL to the MongoDB database.
- `MONGODB_DATABASE_NAME`: Name of the MongoDB database.
- `MONGODB_COLLECTION_NAME`: Name of the MongoDB collection.
- `JWT_SECRET_KEY`: Secret key for JWT token generation.
- `HASHING_ALGORITHM`: Algorithm used for hashing.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time in minutes for the access token.

