from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Game as GameTable
from uirpsoftball.services.game import Game as GameService
from uirpsoftball.services.team import Team as TeamService
from uirpsoftball.schemas import game as game_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    GameTable,
    custom_types.Game.id,
    game_schema.GameAdminCreate,
    game_schema.GameAdminUpdate,
    str
]):
    _PREFIX = '/games'
    _TAG = 'Game'
    _SERVICE = GameService


class GameRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[game_schema.GameExport]:
        return [game_schema.GameExport.model_validate(game) for game in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        game_id: custom_types.Game.id,
    ) -> game_schema.GameExport:
        return game_schema.GameExport.model_validate(
            await cls._get({
                'id': game_id,
            })
        )

    @classmethod
    async def update_score(
        cls,
        game_id: custom_types.Game.id,
        game: game_schema.ScoreUpdate,
    ):
        game_return = await cls._patch({
            'id': game_id,
            'update_model': game_schema.GameAdminUpdate(
                home_team_score=game.home_team_score,
                away_team_score=game.away_team_score,
            )
        })
        async with config.ASYNC_SESSIONMAKER() as session:
            divisions: set[custom_types.Division.id] = set()
            for team_id in [game_return.home_team_id, game_return.away_team_id]:
                if team_id is not None:
                    team = await TeamService.fetch_by_id(session, team_id)
                    if team is not None:
                        division = team.division_id
                        if division is not None:
                            divisions.add(division)

            for division_id in divisions:
                await TeamService.update_seeds(session, division_id)

    @classmethod
    async def update_is_accepting_scores(
        cls,
        game_id: custom_types.Game.id,
        game: game_schema.IsAcceptingScoresUpdate,
    ) -> game_schema.GameExport:
        return game_schema.GameExport.model_validate(
            await cls._patch({
                'id': game_id,
                'update_model': game_schema.GameAdminUpdate(
                    is_accepting_scores=game.is_accepting_scores,
                )
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{game_id}/')(self.by_id)
        self.router.patch('/{game_id}/score/')(self.update_score)
        self.router.patch(
            '/{game_id}/is-accepting-scores/')(self.update_is_accepting_scores)
