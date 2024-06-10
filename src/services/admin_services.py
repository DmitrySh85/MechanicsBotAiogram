from datetime import date, datetime

from db import get_session
from models.models import Schedule, Master, Image, Department
from sqlalchemy import select
from sqlalchemy import and_


async def get_message_from_schedules(department: int):
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    schedules = await get_shedules_from_db(start_of_day, end_of_day, department)
    message_text = await transfer_schedules_to_message_text(schedules)
    return message_text

async def get_shedules_from_db(start_of_day, end_of_day, department):
    async with get_session() as session:
        stmt = select(Master.name, Schedule.time_start, Schedule.time_end).join(Master, Schedule.master == Master.id).filter(and_(Schedule.time_start >= start_of_day, Schedule.time_end <= end_of_day, Master.department == department))
        result = await session.execute(stmt)
    schedules = result.all()
    return schedules

async def transfer_schedules_to_message_text(querys):
    message_text = ""
    for query in querys:
        message_text += f"Мастер {query[0]} начинает смену в {query[1].strftime("%Y-%m-%d %H:%M")}, заканчивает в {query[2].strftime("%Y-%m-%d %H:%M")}.\n"
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
        stmt = select(Image.link, Image.created_at, Master.name).join(Master, Master.id == Image.master).join(Department, Master.department == department).filter(Image.created_at <= end_of_day, Image.created_at >= start_of_day)
        result = await session.execute(stmt)
        return result.all()

def get_result_dict_from_querys(querys):
    results = []
    for query in querys:
        image_link = query[0]
        time_created = query[1].strftime("%Y-%m-%d %H:%M")
        master = query[2]
        text = f"{master} загрузил в {time_created}"
        results.append(
            {"image_link": image_link, "text": text}
        )
    return results