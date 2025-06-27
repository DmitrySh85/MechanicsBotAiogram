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


async def create_vacation(master_id: int) -> None:
    today = datetime.today().date()
    async with get_session() as session:
        for day in range(1, 15):
            d = today + timedelta(days=day)
            stmt = insert(DayOff).values(master=master_id, date=d)
            await session.execute(stmt)
            await session.commit()


async def get_day_offs_for_closest_three_days(master_id: int) -> list[int]:
    today = datetime.today().date()
    start_date = today - timedelta(days=3)
    async with get_session() as session:
        stmt = select(DayOff.id).filter(
            DayOff.date >= start_date,
            DayOff.date <= today,
            DayOff.master == master_id,
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def create_day_off_for_master(master_id: int, day: date) -> DayOff:
    async with get_session() as session:
        day_off = DayOff(master=master_id, date=day)
        session.add(day_off)
        await session.commit()
        await session.refresh(day_off)
        return day_off
