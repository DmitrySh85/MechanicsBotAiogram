from datetime import datetime, timedelta, date

from db import get_session
from services.handlers_services import get_master_id_from_chat_id
from models.models import DayOff
from sqlalchemy import insert, select


async def create_day_off(chat_id: int) -> None:
    master_id = await get_master_id_from_chat_id(chat_id)
    async with get_session() as session:
        stmt = insert(DayOff).values(master=master_id)
        await session.execute(stmt)
        await session.commit()


async def create_day_off_for_master(master_id: int, day: date) -> DayOff:
    async with get_session() as session:
        day_off = DayOff(master=master_id, date=day)
        session.add(day_off)
        await session.commit()
        await session.refresh(day_off)
        return day_off


async def set_day_off_for_masters(masters_ids: list[int], day: date) -> DayOff:
    for master_id in masters_ids:
        await create_day_off_for_master(master_id, day)