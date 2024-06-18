import logging
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn")

class MongoMiddleware(BaseHTTPMiddleware):
    """
    Middleware to integrate MongoDB with FastAPI.

    This middleware initializes a MongoDB client and attaches a specified collection
    to the request state, making it accessible throughout the request lifecycle.

    Attributes:
        client (AsyncIOMotorClient): The MongoDB client.
        db (Database): The MongoDB database.
        collection (Collection): The MongoDB collection.
    """

    def __init__(self, app, db_url, db_name, collection_name):
        """
        Initializes the MongoMiddleware with the given parameters.

        Args:
            app (ASGIApp): The ASGI application.
            db_url (str): The MongoDB connection URL.
            db_name (str): The name of the MongoDB database.
            collection_name (str): The name of the MongoDB collection.
        """
        super().__init__(app)
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        logger.warning("MongoMiddleware initialized")

    async def dispatch(self, request: Request, call_next):
        """
        Attaches the MongoDB collection to the request state and processes the request.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable): The next middleware or route handler.

        Returns:
            Response: The HTTP response.
        """
        logger.warning("Setting up DB in request state")
        request.state.collection = self.collection
        logger.warning(f"Request state: {request.state.collection}")
        response = await call_next(request)
        return response
