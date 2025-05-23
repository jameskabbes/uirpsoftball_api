from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import TournamentGame as TournamentGameTable
from uirpsoftball.services.tournament_game import TournamentGame as TournamentGameService
from uirpsoftball.schemas import tournament_game as tournament_game_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    TournamentGameTable,
    custom_types.Game.id,
    tournament_game_schema.TournamentGameAdminCreate,
    tournament_game_schema.TournamentGameAdminUpdate,
    str
]):
    _PREFIX = '/tournament-games'
    _TAG = 'Tournament Game'
    _SERVICE = TournamentGameService


class TournamentGameRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[tournament_game_schema.TournamentGameExport]:
        return [tournament_game_schema.TournamentGameExport.model_validate(tournament_game) for tournament_game in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        tournament_game_id: custom_types.Game.id,
    ) -> tournament_game_schema.TournamentGameExport:
        return tournament_game_schema.TournamentGameExport.model_validate(
            await cls._get({
                'id': tournament_game_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{tournament_game_id}/')(self.by_id)
