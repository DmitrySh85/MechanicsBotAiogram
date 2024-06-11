import asyncio

from sqlalchemy import insert

from src.db import get_session
from src.models.models import Department


async def create_default_department():
    async with get_session() as session:
        stmt = insert(Department).values(name="default_department")
        await session.execute(stmt)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(create_default_department())