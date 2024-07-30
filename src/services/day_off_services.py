from db import get_session
from services.handlers_services import get_master_id_from_chat_id
from models.models import DayOff
from sqlalchemy import insert


async def create_day_off(chat_id: int) -> None:
    master_id = await get_master_id_from_chat_id(chat_id)
    async with get_session() as session:
        stmt = insert(DayOff).values(master=master_id)
        await session.execute(stmt)
        await session.commit()