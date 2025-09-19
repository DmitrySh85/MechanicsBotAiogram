from datetime import datetime

from db import get_session
from sqlalchemy import select, func
from models.models import Master, Image, DayOff
from .discipline_violation_services import get_masters_with_violations_for_last_month
from .users_services import get_all_masters_names
import logging


async def check_masters_not_send_photo(
        start_time: datetime,
        end_time: datetime,
        category: str
):
    async with get_session() as session:
        subquery = select(
            Master.id).join(
            Image, Image.master == Master.id
            ).filter(
            Image.created_at >= start_time,
            Image.created_at <= end_time,
            Image.category == category
        )
        day_off_query = select(DayOff.master).filter(DayOff.date == func.current_date())
        stmt = select(Master.tg_id).filter(
            ~Master.id.in_(subquery),
            ~Master.id.in_(day_off_query),
            Master.is_manager == False,
            Master.is_blocked == False
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
        stmt = select(Master.name, Master.id).filter(
            ~Master.id.in_(subquery),
            ~Master.id.in_(day_off_query),
            Master.is_manager == False,
            Master.is_blocked == False
                             )
        result = await session.execute(stmt)
    masters_not_send_photo = result.fetchall()
    return masters_not_send_photo


async def get_monthly_report_text():
    violators_query = await get_masters_with_violations_for_last_month()
    violators_names = [master.name for master in violators_query]
    master_names_query = await get_all_masters_names()
    master_names = [master.name for master in master_names_query]
    logging.info(f"{violators_names=}")
    logging.info(f"{master_names=}")
    message_text = "За прошлый месяц:\n"
    masters_list = []
    for name in violators_names:
        masters_list.append(f"{name}❌")
        master_names.remove(name)
    for name in master_names:
        masters_list.append(f"{name}✅")
    masters_list.sort()
    message_text += "\n".join(masters_list)
    return message_text



