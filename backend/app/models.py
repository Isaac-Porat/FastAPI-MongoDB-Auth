from pydantic import BaseModel

class User(BaseModel):
    """
    Represents a user in the system.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
        is_admin (bool): Indicates if the user has admin privileges. Defaults to False.
    """
    username: str
    password: str
    is_admin: bool = False

class Token(BaseModel):
    """
    Represents an authentication token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token (e.g., "bearer").
    """
    access_token: str
    token_type: str