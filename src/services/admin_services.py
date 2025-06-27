from datetime import date, datetime
from time import strptime
from typing import List

import pytz
from db import get_session
from models.models import Schedule, Master, Image, Department, DayOff, DisciplineViolation
from sqlalchemy import select, func, exists, insert, delete
from .discipline_violation_services import (
    get_discipline_violations_for_current_month,
    get_discipline_violations_for_last_month
)
from settings import START_WORK_TIME, END_WORK_TIME


async def get_message_from_schedules(department: int):
    working_masters_names = await get_working_masters_names()
    message_text = transfer_working_masters_names_to_message_text(working_masters_names)
    return message_text


async def get_working_masters_names() -> List[str]:
    today = datetime.today().date()
    async with get_session() as session:
        subquery = select(DayOff.master).where(DayOff.date == today)
        stmt = select(Master.name).filter(
            Master.is_manager == False,
            Master.is_blocked == False,
            ~Master.id.in_(subquery)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

def transfer_working_masters_names_to_message_text(working_masters_names) -> str:
    message_text = "Сегодня работают:\n" + "\n".join(working_masters_names)
    return message_text


async def create_missing_schedules(department: int) -> None:
    no_schedule_masters = await get_no_schedule_masters(department)
    if no_schedule_masters:
        await create_schedules_for_masters(no_schedule_masters)


async def get_no_schedule_masters(department: int) -> List[int]:
    async with get_session() as session:
        subquery = select(
            Master.id).join(Schedule, Master.id == Schedule.master)
        stmt = select(
            Master.id).where(Master.id.not_in(subquery)
                    ).filter(
            Master.is_blocked == False,
            Master.is_manager == False,
            Master.is_manager == False
                                       )
        result = await session.execute(stmt)
        return result.scalars().all()


async def create_schedules_for_masters(masters: List[int]) -> None:
    async with get_session() as session:
        for master in masters:
            start_time = datetime.strptime(START_WORK_TIME, "%H:%M:%S").time()
            end_time = datetime.strptime(END_WORK_TIME, "%H:%M:%S").time()
            stmt = insert(Schedule).values(
                master=master,
                time_start=start_time,
                time_end=end_time,
            )
            await session.execute(stmt)
            await session.commit()


async def get_message_from_photos(department: int):
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    querys = await get_images_from_db(start_of_day, end_of_day, department)
    results = get_result_dict_from_querys(querys)
    return results


async def get_images_from_db(start_of_day, end_of_day, department):
    async with get_session() as session:
        stmt = (
            select(Image.link, Image.created_at, Master.name)
            .distinct().join(Master, Master.id == Image.master)
            .join(Department, Master.department == department)
            .filter(Image.created_at <= end_of_day, Image.created_at >= start_of_day)
            .order_by(Master.name)
        )
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


async def get_discipline_violation_text():
    discipline_violations_for_current_month = await get_discipline_violations_for_current_month()
    if not discipline_violations_for_current_month:
        this_month_violations = "За данный месяц нет нарушений дисциплины."
    else:
        this_month_violations = "Нарушения дисциплины за данный месяц:\n"
        this_month_violations += "".join(
            ([f"{violation.date} {violation.name}\n" for violation in discipline_violations_for_current_month]))
    discipline_violations_for_last_month = await get_discipline_violations_for_last_month()
    if not discipline_violations_for_last_month:
        last_month_violations = "За прошлый месяц не было нарушений дисциплины."
    else:
        last_month_violations = "Нарушения дисциплины за прошлый месяц:\n"
        last_month_violations += "".join(
            ([f"{violation.date} {violation.name}\n" for violation in discipline_violations_for_last_month]))

    return f"{this_month_violations}\n{last_month_violations}"


async def get_available_masters() -> dict[int, str]:
    async with get_session() as session:
        stmt = select(Master.id, Master.name).where(
            Master.is_blocked == False,
            Master.is_manager == False
        )
        result = await session.execute(stmt)
        return {r.id: r.name for r in result.fetchall()}


async def delete_selected_masters(masters_ids: list[int]) -> None:
    async with get_session() as session:
        stmt = delete(Schedule).where(Schedule.master.in_(masters_ids))
        await session.execute(stmt)
        await session.commit()

        stmt = delete(DayOff).where(DayOff.master.in_(masters_ids))
        await session.execute(stmt)
        await session.commit()

        stmt = delete(Image).where(Image.master.in_(masters_ids))
        await session.execute(stmt)
        await session.commit()

        stmt = delete(DisciplineViolation).where(DisciplineViolation.master.in_(masters_ids))
        await session.execute(stmt)
        await session.commit()

        stmt = delete(Master).where(Master.id.in_(masters_ids))
        await session.execute(stmt)
        await session.commit()


async def get_working_masters_chats_ids() -> list[int]:
    today = datetime.today().date()
    async with get_session() as session:
        subquery = select(DayOff.master).where(DayOff.date == today)
        stmt = select(Master.tg_id).filter(
            Master.is_blocked == False,
            ~Master.id.in_(subquery),
            Master.is_manager == False
        )
        result = await session.execute(stmt)
        return result.scalars().all()