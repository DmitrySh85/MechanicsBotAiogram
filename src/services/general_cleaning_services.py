from typing import TypedDict

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from db import get_session
from datetime import datetime
from models.models import GeneralCleaning
from sqlalchemy import select
from services.users_services import get_manager_tg_ids_from_db
from services.handlers_services import get_master
from static_data.static_data import GENERAL_CLEANING_CHECKLIST
from services.admin_services import get_last_images


class GeneralCleaningDict(TypedDict):
    id: int
    date: datetime


async def get_or_create_general_cleaning(date: datetime.date) -> GeneralCleaning:
    general_cleaning = await get_general_cleaning(date)
    if not general_cleaning:
        general_cleaning = await create_general_cleaning(date)
    return general_cleaning


async def get_general_cleaning(date: datetime.date) -> GeneralCleaning | None:
    async with get_session() as session:
        stmt = select(GeneralCleaning).where(GeneralCleaning.date == date)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()


async def create_general_cleaning(date: datetime.date) -> GeneralCleaning:
    async with get_session() as session:
        general_cleaning = GeneralCleaning(
            date=date
        )
        session.add(general_cleaning)
        await session.commit()
        await session.refresh(general_cleaning)
        return general_cleaning


async def send_general_cleaning_photos_to_admin(
        bot: Bot,
        tg_id: int
) -> None:
    admin_tg_ids = await get_manager_tg_ids_from_db()
    master = await get_master(tg_id)
    master_name = master.name
    images_links = await get_last_images(master.id, len(GENERAL_CLEANING_CHECKLIST))
    for admin_tg_id in admin_tg_ids:
        await bot.send_message(
            admin_tg_id,
            f"{master_name} закончил генеральную уборку."
        )
        await bot.send_media_group(
            admin_tg_id,
            [InputMediaPhoto(media=FSInputFile(image_link)) for image_link in images_links]
        )


async def get_general_cleanings(date: datetime.date) -> list[GeneralCleaningDict]:
    async with get_session() as session:
        stmt = select(GeneralCleaning.id, GeneralCleaning.date).where(GeneralCleaning.date >= date)
        result = await session.execute(stmt)
        return [GeneralCleaningDict(id=gc.id, date=gc.date) for gc in result.fetchall()]