import logging
from typing import TypedDict, NamedTuple

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from db import get_session
from datetime import datetime, time
from models.models import GeneralCleaning, Image, Master
from sqlalchemy import select, desc
from services.users_services import get_manager_tg_ids_from_db
from services.handlers_services import get_master
from static_data.static_data import GENERAL_CLEANING_CHECKLIST
from services.admin_services import get_last_images


class GeneralCleaningDict(TypedDict):
    id: int
    date: datetime


class ImageData(NamedTuple):
    link: str
    created_at: datetime
    category: str


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
    images_items = await get_general_cleaning_images_with_category(master.id, len(GENERAL_CLEANING_CHECKLIST))
    for admin_tg_id in admin_tg_ids:
        await bot.send_message(
            admin_tg_id,
            f"{master_name} закончил генеральную уборку."
        )
        for image in images_items:
            caption = f"{master_name}: {image.category}"
            try:
                await bot.send_photo(
                    admin_tg_id,
                    photo=FSInputFile(image.link),
                    caption=caption
                )
            except Exception as e:
                logging.warning(e)


async def get_general_cleanings(date: datetime.date) -> list[GeneralCleaningDict]:
    async with get_session() as session:
        stmt = select(GeneralCleaning.id, GeneralCleaning.date).where(GeneralCleaning.date >= date)
        result = await session.execute(stmt)
        return [GeneralCleaningDict(id=gc.id, date=gc.date) for gc in result.fetchall()]


async def get_general_cleaning_images_with_category(
        master_id: int,
        limit: int
) -> list[ImageData]:
    async with get_session() as session:
        stmt = select(
            Image.link,
            Image.created_at,
            Image.category
        ).distinct(
        ).join(
            Master, Master.id == Image.master
        ).filter(
            Master.id == master_id,
        ).order_by(desc("created_at")).limit(limit)
        result = await session.execute(stmt)
        return result.fetchall()


async def get_general_cleaning_images_with_category_for_date(
    date: datetime.date,
) -> list[ImageData]:
    start_dt = datetime.combine(date, time(0, 0, 0))
    end_dt = datetime.combine(date, time(23, 59, 59))
    async with get_session() as session:
        stmt = select(
            Image.link,
            Master.name,
            Image.category
        ).distinct(
        ).join(
            Master, Master.id == Image.master
        ).filter(
            Image.created_at >= start_dt,
            Image.created_at <= end_dt,
            ~Image.category.in_(["Начало рабочего дня", "Завершение рабочего дня"])
        ).order_by(desc("name"))
        result = await session.execute(stmt)
        return result.fetchall()