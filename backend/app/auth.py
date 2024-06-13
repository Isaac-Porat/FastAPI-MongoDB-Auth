from datetime import timedelta, datetime
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from crud import authenticate_user, create_user
from config import JWT_SECRET_KEY, HASHING_ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=HASHING_ALGORITHM)

    return encoded_jwt

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
  user = create_user(form_data.username, form_data.password)
  if not user:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Incorrect username or password",
          headers={"WWW-Authenticate": "Bearer"},
      )
  access_token = create_access_token(data={"sub": user.email})
  return {"access_token": access_token, "token_type": "bearer"}

async def register_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
  user = authenticate_user(form_data.username, form_data.password)
  if not user:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Incorrect username or password",
          headers={"WWW-Authenticate": "Bearer"},
      )
  access_token = create_access_token(data={"sub": user.email})
  return {"access_token": access_token, "token_type": "bearer"}

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
