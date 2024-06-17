import logging
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn")

class MongoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_url, db_name, collection_name):
        super().__init__(app)
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        logger.warning("MongoMiddleware initialized")

    async def dispatch(self, request: Request, call_next):
        logger.warning("Setting up DB in request state")
        request.state.collection = self.collection
        logger.warning(f"Request state: {request.state.collection}")
        response = await call_next(request)
        return response
