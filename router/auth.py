from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Users
from typing import Annotated
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from dependencies import db_dependency
from schemas import CreateUser
from starlette import status


router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "1f5addbb2c42310e424a1d515e7da5a8a731249bd3728fa449078df86d41aa69"
ALGORITHM = "HS256"

def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return False

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token_to_get_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        return {"username": username, "id": user_id}
    except:
        raise JWTError

user_dependency = Annotated[dict, Depends(decode_token_to_get_user)]

@router.post("/auth/login")
def user_login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=404, detail="Failed Authentication")

    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/register")
def create_user(db: db_dependency, new_user: CreateUser):

    user_model = Users(
        username = new_user.username,
        email = new_user.email,
        hashed_password = bcrypt_context.hash(new_user.password)
    )

    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"Message": "User Created Successfully"})

