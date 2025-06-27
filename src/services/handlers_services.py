import os
from datetime import time, datetime, timezone, timedelta

import pytz
from aiogram.types import Message
from db import get_session
from models.models import Master, Image, Schedule
from sqlalchemy import select, insert
from settings import START_WORK_TIME, END_WORK_TIME
import logging


async def save_image(message: Message):
    try:
        image_link = await save_image_to_hdd(message)
        chat_id = message.chat.id
        master_id = await get_master_id_from_chat_id(chat_id)
        await add_image_link_to_db(image_link, master_id)
    except Exception as e:
        logging.info(e)


async def save_image_to_hdd(message):
    photo = message.photo[-1]
    if not os.path.exists("images"):
        os.makedirs("images")
    file_path = (f"images/{photo.file_id}.jpg")
    await message.bot.download(file=message.photo[-1].file_id, destination=file_path)
    return file_path


async def add_image_link_to_db(image_link, master_id):
    async with get_session() as session:
        stmt = insert(Image).values(
            master=master_id,
            link=image_link,
            created_at=datetime.now(tz=pytz.timezone("Europe/Moscow"))
        )
        await session.execute(stmt)
        await session.commit()


async def get_master_id_from_chat_id(chat_id):
    async with get_session() as session:
        stmt = select(Master.id).where(Master.tg_id == chat_id)
        master_id = await session.scalar(stmt)
    return master_id


async def get_master(chat_id: int):
    async with get_session() as session:
        stmt = select(Master).where(Master.tg_id == chat_id)
        result = await session.scalar(stmt)
        return result


async def create_master_and_schedule(message: Message):
    name = message.from_user.full_name
    chat_id = message.chat.id
    created_master_id = await create_master(name, chat_id)
    await create_schedule_for_master(created_master_id)


async def create_master(name, chat_id):
    async with get_session() as session:
        stmt = insert(Master).values(
            name=name,
            tg_id=chat_id,
            department=1,
            is_manager=False
        )
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(select(Master).filter_by(name=name, tg_id=chat_id))
        created_master = result.scalar()
        created_master_id = created_master.id
        return created_master_id

async def create_schedule_for_master(created_master_id):
    async with get_session() as session:
        time_start = convert_string_to_time(START_WORK_TIME)
        time_end = convert_string_to_time(END_WORK_TIME)
        stmt = insert(Schedule).values(
            master=created_master_id,
            time_start=time_start,
            time_end=time_end
        )
        await session.execute(stmt)
        await session.commit()


def convert_string_to_time(string: str) ->time:
    return time(hour=int(string[0:2]), minute=int(string[3:5]))


def convert_string_to_time_with_offset(string: str, offset: str) -> time:
    t = datetime.strptime(string, '%H:%M:%S')
    result = t + timedelta(minutes=int(offset))
    return result.time()