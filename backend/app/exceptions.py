import logging

logger = logging.getLogger("uvicorn")

class UsernameAlreadyExistsException(Exception):
    """
    Exception raised when a username already exists in the database.

    Attributes:
        username (str): The username that already exists.
        message (str): The error message to be displayed.
    """
    def __init__(self, username, message="Username already exists"):
        """
        Initializes the UsernameAlreadyExistsException with the given username and message.

        Args:
            username (str): The username that already exists.
            message (str, optional): The error message to be displayed. Defaults to "Username already exists".
        """
        self.username = username
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """
        Returns the string representation of the exception.

        Returns:
            str: The error message with the username.
        """
        return f"{self.message}: {self.username}"

async def check_username_exists(collection, username):
    """
    Checks if a username already exists in the database.

    Args:
        collection (Collection): The MongoDB collection to search in.
        username (str): The username to check for existence.

    Raises:
        UsernameAlreadyExistsException: If the username already exists in the database.
    """
    result = await collection.find_one({"username": username})
    if result is not None and username == result["username"]:
        raise UsernameAlreadyExistsException(username)