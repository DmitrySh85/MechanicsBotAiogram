from datetime import datetime

from db import get_session
from sqlalchemy import insert, select, func
from models.models import DisciplineViolation, Master


async def create_discipline_violation(master_id: int) -> None:
    async with get_session() as session:
        stmt = insert(DisciplineViolation).values(master=master_id)
        await session.execute(stmt)
        await session.commit()


async def get_discipline_violations_for_current_month():
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    async with get_session() as session:
        stmt = select(DisciplineViolation.date, Master.name).join(
            Master, DisciplineViolation.master == Master.id
        ).filter(
            func.extract('year', DisciplineViolation.date) == current_year,
            func.extract('month', DisciplineViolation.date) == current_month,
            Master.is_manager == False
        )
        result = await session.execute(stmt)
        violations = result.fetchall()
        return violations


async def get_discipline_violations_for_last_month():
    now = datetime.now()
    if now.month == 1:
        last_month = 12
        last_year = now.year - 1
    else:
        last_month = now.month - 1
        last_year = now.year
    async with get_session() as session:
        stmt = select(DisciplineViolation.date, Master.name).join(
            Master, DisciplineViolation.master == Master.id
        ).filter(
            func.extract('year', DisciplineViolation.date) == last_year,
            func.extract('month', DisciplineViolation.date) == last_month,
            Master.is_manager == False
        )
        result = await session.execute(stmt)
        violations = result.fetchall()
        return violations


async def get_masters_with_violations_for_last_month():
    now = datetime.now()

    if now.month == 1:
        last_month = 12
        last_year = now.year - 1
    else:
        last_month = now.month - 1
        last_year = now.year
    async with get_session() as session:
        stmt = select(Master.name, func.count(DisciplineViolation.id)).join(
            DisciplineViolation, DisciplineViolation.master == Master.id
        ).filter(
            func.extract('year', DisciplineViolation.date) == last_year,
            func.extract('month', DisciplineViolation.date) == last_month,
            Master.is_manager == False,
            Master.is_blocked == False
        ).group_by(Master.name)
        result = await session.execute(stmt)
        names = result.fetchall()
    return names
