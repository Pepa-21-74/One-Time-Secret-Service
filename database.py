from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_async_engine(database_url)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_db)]
