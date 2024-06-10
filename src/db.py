from contextlib import asynccontextmanager

from sqlalchemy import NullPool, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import DB_URL


Base = declarative_base()

engine = create_async_engine(DB_URL, poolclass=NullPool)

@asynccontextmanager
async def get_session():
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        yield session

