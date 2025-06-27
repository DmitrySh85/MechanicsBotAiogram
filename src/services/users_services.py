from db import get_session

from models.models import Master
from services.handlers_services import get_master
from sqlalchemy import update, select


async def register_user(tg_id: int, username: str):
    master = await get_master(tg_id)
    print("MASTER", master)
    if not master:
        await insert_master_to_db(tg_id, username)
    else:
        raise ValueError(f"Master {master.id} is already registered")


async def insert_master_to_db(tg_id: int, username: str):
    async with get_session() as session:
        master = Master(
            tg_id=tg_id,
            name=username,
            department=1
        )
        session.add(master)
        await session.commit()
        await session.refresh(master)


async def reject_user(tg_id: int, username: str):
    master = await get_master(tg_id)
    if master:
        return await set_master_is_blocked(tg_id)
    await insert_blocked_master_to_db(tg_id, username)


async def set_master_is_blocked(tg_id: int):
    async with get_session() as session:
        stmt = update(Master).where(Master.id == tg_id).values(is_blocked=True)
        await session.execute(stmt)
        await session.commit()


async def insert_blocked_master_to_db(tg_id: int, username: str):
    async with get_session() as session:
        master = Master(
            tg_id=tg_id,
            name=username,
            is_blocked=True
        )
        session.add(master)
        await session.commit()


async def get_manager_tg_ids_from_db():
    async with get_session() as session:
        stmt = select(Master.tg_id).where(
            Master.is_manager == True
        )
        result = await session.execute(stmt)
    admin_list = result.fetchall()
    return [tg_id.tg_id for tg_id in admin_list]


async def update_username(user_id: int, username: str) -> None:
    async with get_session() as session:
        stmt = update(Master).values(name=username).where(Master.id == user_id)
        await session.execute(stmt)
        await session.commit()


async def get_all_masters_names():
    async with get_session() as session:
        stmt = select(Master.name).where(Master.is_manager == False)
        result = await session.execute(stmt)
    return result.fetchall()

