import os

from aiogram.types import Message
from db import get_session
from models.models import Master, Image
from sqlalchemy import select, insert


async def save_image(message: Message):
    image_link = await save_image_to_hdd(message)
    chat_id = message.chat.id
    master_id = await get_master_id_from_chat_id(chat_id)
    await add_image_link_to_db(image_link, master_id)


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
            link=image_link
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

