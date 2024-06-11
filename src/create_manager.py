import asyncio

from sqlalchemy import update, select, insert
from sqlalchemy.exc import DBAPIError

from db import get_session
from models.models import Master
from time import sleep


async def create_manager():
    tg_id = input("Введите telegram id: ")
    name = input("Введите имя: ")
    async with get_session() as session:
        try:
            stmt = select(Master.id).where(Master.tg_id == int(tg_id))
            result = await session.execute(stmt)
        except DBAPIError:
            print("Неправильный telegram_id")
            sleep(10)
            return
        except ValueError:
            print("Неправильный telegram_id")
            sleep(10)
            return
        master_id = result.scalar()
    if master_id:
        async with get_session() as session:
            stmt = update(Master).values(
                is_manager=True, name=name
            ).where(Master.id == master_id)
            await session.execute(stmt)
            await session.commit()
        print("Данные профиля успешно изменены")
        sleep(10)
        return
    async with get_session() as session:
        stmt = insert(Master).values(
            name=name,
            tg_id=int(tg_id),
            is_manager=True,
            department=1
        )
        await session.execute(stmt)
        await session.commit()
    print("Менеджер успешно зарегистрирован")
    sleep(10)
    return


if __name__ == "__main__":
    asyncio.run(create_manager())