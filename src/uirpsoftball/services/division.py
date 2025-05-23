from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import Sequence

from uirpsoftball import custom_types
from uirpsoftball.models.tables import Division as DivisionTable
from uirpsoftball.services import base, team as team_service, division as division_service
from uirpsoftball.schemas import division as division_schema, pagination as pagination_schema
import random

class Division(
    base.Service[
        DivisionTable,
        custom_types.Division.id,
        division_schema.DivisionAdminCreate,
        division_schema.DivisionAdminUpdate,
        str],
    base.SimpleIdModelService[
        DivisionTable,
        custom_types.Division.id,
    ]
):
    _MODEL = DivisionTable


    @classmethod
    async def shuffle(cls, session: AsyncSession):

        teams = await team_service.Team.fetch_many(session, pagination=pagination_schema.Pagination(limit=1000,offset=0))
        divisions = await division_service.Division.fetch_many(session, pagination=pagination_schema.Pagination(limit=1000,offset=0))

        n = len(teams) // len(divisions)
        extra = len(teams) % len(divisions)

        division_assingments = []
        for division in divisions:
            division_assingments.extend([division_service.Division.model_id(division)] * n)

        for i in range(extra):
            division_assingments.append(division_service.Division.model_id(divisions[i]))

        random.shuffle(division_assingments)

        for team in teams:
            team.division_id = division_assingments.pop()

        session.add_all(teams)
        await session.commit()