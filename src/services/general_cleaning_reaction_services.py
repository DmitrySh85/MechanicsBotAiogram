from typing import NamedTuple

from db import get_session
from models.models import GeneralCleaningReaction, Master, GeneralCleaning
from sqlalchemy import update, select


class Reaction(NamedTuple):
    is_confirmed: bool
    text: str
    name: str

async def create_general_cleaning_reaction(
        general_cleaning_id: int,
        is_confirmed: bool,
        master_id: int
) -> GeneralCleaningReaction:
    async with get_session() as session:
        reaction = GeneralCleaningReaction(
            general_cleaning=general_cleaning_id,
            is_confirmed=is_confirmed,
            master=master_id,
        )
        session.add(reaction)
        await session.commit()
        await session.refresh(reaction)
        return reaction


async def update_general_cleaning_reaction_with_text(
        reaction_id: int,
        text: str
) -> None:
    async with get_session() as session:
        stmt = update(
            GeneralCleaningReaction
            ).values(
            text=text
        ).where(GeneralCleaningReaction.id == reaction_id)
        await session.execute(stmt)
        await session.commit()


async def get_general_cleaning_reactions(general_cleaning_id: int) -> list[Reaction]:
    async with get_session() as session:
        stmt = select(
            GeneralCleaningReaction.is_confirmed,
            GeneralCleaningReaction.text,
            Master.name
        ).join(
            Master, GeneralCleaningReaction.master == Master.id
        ).join(
            GeneralCleaning, GeneralCleaningReaction.general_cleaning == GeneralCleaning.id
        ).where(GeneralCleaning.id == general_cleaning_id)
        result = await session.execute(stmt)
        return result.fetchall()


def process_reactions_to_text(reactions: list[Reaction]) -> str:
    positive_reactions = []
    negative_reactions = []
    for reaction in reactions:
        if reaction.is_confirmed:
            positive_reactions.append(reaction)
        else:
            negative_reactions.append(reaction)
    positiive_reaction_text = "Согласны:\n" + "\n".join([reaction.name for reaction in positive_reactions])
    negative_reaction_text = "Не согласны:\n" + "\n".join(
        [f"{reaction.name} ```Комментарий: {reaction.text}```" for reaction in negative_reactions]
    )
    return positiive_reaction_text + "\n"  + negative_reaction_text

