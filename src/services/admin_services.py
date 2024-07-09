from datetime import date, datetime

import pytz
from db import get_session
from models.models import Schedule, Master, Image, Department
from sqlalchemy import select, func


async def get_message_from_schedules(department: int):
    schedules = await get_shedules_from_db(department)
    message_text = await transfer_schedules_to_message_text(schedules)
    return message_text


async def get_shedules_from_db(department):
    async with get_session() as session:
        stmt = select(Master.name, Schedule.time_start, Schedule.time_end).join(Master, Schedule.master == Master.id).filter(Master.department == department)
        result = await session.execute(stmt)
    schedules = result.all()
    return schedules


async def transfer_schedules_to_message_text(querys):
    message_text = ""
    for query in querys:
        master_name = query[0]
        time_start = query[1].strftime("%H:%M")
        time_end = query[2].strftime("%H:%M")
        message_text += f"Мастер {master_name} начинает смену в {time_start}, заканчивает в {time_end}.\n"
    return message_text


async def get_message_from_photos(department):
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    querys = await get_images_from_db(start_of_day, end_of_day, department)
    results = get_result_dict_from_querys(querys)
    return results


async def get_images_from_db(start_of_day, end_of_day, department):
    async with get_session() as session:
        stmt = select(Image.link, Image.created_at, Master.name).distinct().join(Master, Master.id == Image.master).join(Department, Master.department == department).filter(Image.created_at <= end_of_day, Image.created_at >= start_of_day)
        result = await session.execute(stmt)
        return result.all()


def get_result_dict_from_querys(querys):
    results = []
    for query in querys:
        image_link = query[0]
        utc_time = query[1]
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_time = utc_time.astimezone(moscow_tz)
        time_created = moscow_time.strftime("%Y-%m-%d %H:%M")
        master = query[2]
        text = f"{master} загрузил в {time_created}"
        results.append(
            {"image_link": image_link, "text": text}
        )
    return results

def parse_date_from_message_text(text: str) -> date:
    return datetime.strptime(text, "%d-%m-%Y")


async def get_images_and_messages_for_the_date(date: datetime):
    querys = await get_images_for_the_date(date)
    results = get_result_dict_from_querys(querys)
    return results


async def get_images_for_the_date(selected_date: datetime):
    async with get_session() as session:
        stmt = select(Image.link, Image.created_at, Master.name).distinct().join(
            Master, Master.id == Image.master
        ).filter(
            func.DATE(Image.created_at) == selected_date
        )
        result = await session.execute(stmt)
        images = result.all()
    return images