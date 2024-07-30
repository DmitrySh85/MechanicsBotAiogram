from db import get_session
from sqlalchemy import select, func
from models.models import Master, Image, DayOff


async def check_masters_not_send_photo(start_time, end_time):
    async with get_session() as session:
        subquery = select(
            Master.id).join(Image, Image.master == Master.id
                            ).filter(
            Image.created_at >= start_time,
            Image.created_at <= end_time,
        )
        day_off_query = select(DayOff.master).filter(DayOff.date == func.current_date())
        stmt = select(Master.tg_id).filter(
            ~Master.id.in_(subquery),
            ~Master.id.in_(day_off_query),
            Master.is_manager == False
                             )
        result = await session.execute(stmt)
    masters_not_send_photo = result.fetchall()
    return masters_not_send_photo


async def check_master_names_not_send_photo(start_time, end_time):
    async with get_session() as session:
        subquery = select(
            Master.id).join(Image, Image.master == Master.id
                            ).filter(
            Image.created_at >= start_time,
            Image.created_at <= end_time,
        )
        day_off_query = select(DayOff.master).filter(DayOff.date == func.current_date())
        stmt = select(Master.name).filter(
            ~Master.id.in_(subquery),
            ~Master.id.in_(day_off_query),
            Master.is_manager == False
                             )
        result = await session.execute(stmt)
    masters_not_send_photo = result.fetchall()
    return masters_not_send_photo
