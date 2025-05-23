from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Tournament as TournamentTable
from uirpsoftball.services.tournament import Tournament as TournamentService
from uirpsoftball.schemas import tournament as tournament_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    TournamentTable,
    custom_types.Tournament.id,
    tournament_schema.TournamentAdminCreate,
    tournament_schema.TournamentAdminUpdate,
    str
]):
    _PREFIX = '/tournaments'
    _TAG = 'Tournament'
    _SERVICE = TournamentService


class TournamentRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[tournament_schema.TournamentExport]:
        return [tournament_schema.TournamentExport.model_validate(tournament) for tournament in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        tournament_id: custom_types.Tournament.id,
    ) -> tournament_schema.TournamentExport:
        return tournament_schema.TournamentExport.model_validate(
            await cls._get({
                'id': tournament_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{tournament_id}/')(self.by_id)
