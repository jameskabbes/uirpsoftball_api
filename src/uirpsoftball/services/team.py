from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from uirpsoftball import custom_types, config
from uirpsoftball.services import base
from uirpsoftball.models.tables import Team as TeamTable
from uirpsoftball.schemas import team as team_schema, pagination as pagination_schema

from collections.abc import Sequence

class Team(
    base.Service[
        TeamTable,
        custom_types.Team.id,
        team_schema.TeamAdminCreate,
        team_schema.TeamAdminUpdate,
        str],
    base.SimpleIdModelService[
        TeamTable,
        custom_types.Team.id,
    ]
):
    _MODEL = TeamTable

    @classmethod
    async def id_from_slug(cls, session: AsyncSession, slug: custom_types.Team.slug) -> custom_types.Team.id | None:

        team = await cls.fetch_one(session, select(cls._MODEL).where(cls._MODEL.slug == slug))
        if team is None:
            return None
        else:
            return cls.model_id(team)
            
    @staticmethod
    def is_real(team_id: custom_types.Team.id) -> bool:
        return team_id >= 0

    @classmethod
    async def fetch_many_by_division(cls, session: AsyncSession, division_id: custom_types.Division.id, pagination: pagination_schema.Pagination ) -> Sequence[TeamTable]:

        return await cls.fetch_many(
            session,
            pagination=pagination,
            query=select(cls._MODEL).where(cls._MODEL.division_id == division_id)
        )

