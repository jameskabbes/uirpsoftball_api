from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Team as TeamTable
from uirpsoftball.services.team import Team as TeamService
from uirpsoftball.schemas import team as team_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    TeamTable,
    custom_types.Team.id,
    team_schema.TeamAdminCreate,
    team_schema.TeamAdminUpdate,
    str
]):
    _PREFIX = '/teams'
    _TAG = 'Team'
    _SERVICE = TeamService


class TeamRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[team_schema.TeamExport]:
        return [team_schema.TeamExport.model_validate(team) for team in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        team_id: custom_types.Team.id,
    ) -> team_schema.TeamExport:
        return team_schema.TeamExport.model_validate(
            await cls._get({
                'id': team_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{team_id}')(self.by_id)
