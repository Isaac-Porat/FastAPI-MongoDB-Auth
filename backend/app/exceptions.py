import logging

logger = logging.getLogger("uvicorn")

class UsernameAlreadyExistsException(Exception):
    def __init__(self, username, message="Username already exists"):
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.username}"

async def check_username_exists(collection, username):
    result = await collection.find_one({"username": username})
    if result is not None and username == result["username"]:
        raise UsernameAlreadyExistsException(username)