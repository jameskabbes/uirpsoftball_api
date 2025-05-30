from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from uirpsoftball import custom_types, config
from uirpsoftball.services import base, game as game_service
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
    async def fetch_many_by_division(cls, session: AsyncSession, division_id: custom_types.Division.id, pagination: pagination_schema.Pagination) -> Sequence[TeamTable]:

        return await cls.fetch_many(
            session,
            pagination=pagination,
            query=select(cls._MODEL).where(
                cls._MODEL.division_id == division_id)
        )

    @classmethod
    async def rank_by_division(cls, session: AsyncSession, division_id: custom_types.Division.id, pagination: pagination_schema.Pagination) -> Sequence[custom_types.Team.id]:

        teams = await cls.fetch_many_by_division(session, division_id, pagination)
        ranked_teams = sorted(
            teams,
            key=lambda team: team.seed,
            reverse=True
        )

        return [ranked_team.id for ranked_team in ranked_teams]

    @classmethod
    async def calculate_statistics(cls, session: AsyncSession, team_ids: Sequence[custom_types.Team.id]) -> dict[custom_types.Team.id, team_schema.TeamStatisticsExport]:

        statistics_by_team_id: dict[custom_types.Team.id,
                                    team_schema.TeamStatisticsExport] = {}

        for team_id in team_ids:
            statistics_by_team_id[team_id] = team_schema.TeamStatisticsExport(
                run_differential=0,
                game_ids_won=set(),
                game_ids_lost=set()
            )

        games = await game_service.Game.fetch_many(
            session,
            pagination=pagination_schema.Pagination(limit=1000, offset=0),
            query=select(game_service.Game._MODEL).where(
                col(game_service.Game._MODEL.home_team_id).in_(team_ids) |
                col(game_service.Game._MODEL.away_team_id).in_(team_ids)
            ).where(col(game_service.Game._MODEL.away_team_score).is_not(None) & col(game_service.Game._MODEL.home_team_score).is_not(None))
        )

        for game in games:
            if game.home_team_id is not None and game.away_team_id is not None and game.home_team_score is not None and game.away_team_score is not None:

                if game.home_team_id in statistics_by_team_id:
                    statistics_by_team_id[game.home_team_id].run_differential += game.home_team_score - \
                        game.away_team_score

                    if game.home_team_score > game.away_team_score:
                        statistics_by_team_id[game.home_team_id].game_ids_won.add(
                            game.id)
                    if game.home_team_score < game.away_team_score:
                        statistics_by_team_id[game.home_team_id].game_ids_lost.add(
                            game.id)

                if game.away_team_id in statistics_by_team_id:
                    statistics_by_team_id[game.away_team_id].run_differential += game.away_team_score - \
                        game.home_team_score

                    if game.away_team_score > game.home_team_score:
                        statistics_by_team_id[game.away_team_id].game_ids_won.add(
                            game.id)
                    if game.away_team_score < game.home_team_score:
                        statistics_by_team_id[game.away_team_id].game_ids_lost.add(
                            game.id)

        return statistics_by_team_id
