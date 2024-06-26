from db import get_session
from sqlalchemy import select
from models.models import Master, Image


async def check_masters_not_send_photo(start_time, end_time):

    async with get_session() as session:
        subquery = select(Master.id).join(Image, Image.master == Master.id).filter(
            Image.created_at >= start_time,
            Image.created_at <= end_time
        )
        stmt = select(Master.tg_id).filter(
            ~Master.id.in_(subquery),
            Master.is_manager == False
        )
        result = await session.execute(stmt)
    masters_not_send_photo = result.fetchall()
    return masters_not_send_photo



