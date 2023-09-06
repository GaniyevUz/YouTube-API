import typing as t
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import Integer, DateTime, func, String, ForeignKey, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, relationship, mapped_column
from starlette import status

class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=func.current_timestamp())


class User(Base):
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    tokens: Mapped[list['Token']] = relationship(back_populates='user', lazy='select', cascade='all, delete')


class Token(Base):
    id = None
    token: Mapped[str] = mapped_column(String(255), unique=True, default=str(uuid4()), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=100)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='tokens')

    @classmethod
    async def get_or_404(cls, db: AsyncSession, **kwargs):
        try:
            user = (await db.execute(select(cls).filter_by(**kwargs))).scalars().one_or_none()
            if user is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, 'detail not found')
            return user
        except NoResultFound as e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, e)

    @classmethod
    async def update(cls, form, db: AsyncSession, **kwargs):
        data = await cls.get_or_404(db, **kwargs)
        query = update(cls).filter_by(**kwargs).values(**form)
        await db.execute(query)
        await db.commit()
        await db.refresh(data)
        return data
