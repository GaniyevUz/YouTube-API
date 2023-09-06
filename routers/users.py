import os
from json import loads

from dotenv import load_dotenv
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database import get_db
from models import User, Token

load_dotenv()
API_KEY = os.getenv('API_KEY')

users = APIRouter(prefix='/users', tags=['users'])


class UserFormModel(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(cls, username: str = Body(...), password: str = Body(...)):
        return cls(username=username, password=password)


@users.post('/sign-up')
async def sign_up(form: UserFormModel = Depends(UserFormModel.as_form),
                  db: AsyncSession = Depends(get_db)):
    person = loads(form.json())
    user = User(**person)
    try:
        db.add(user)
        await db.commit()
        token = Token(user_id=user.id)
        db.add(token)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return user.__dict__ | {'token': token.token}
