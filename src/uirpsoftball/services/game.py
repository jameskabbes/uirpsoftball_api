from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col, func
from collections.abc import Sequence
from typing import Literal
import datetime as datetime_module

from uirpsoftball import custom_types, config
from uirpsoftball.services import base, location as location_service
from uirpsoftball.models.tables import Game as GameTable
from uirpsoftball.schemas import game as game_schema, pagination as pagination_schema


class Game(
    base.Service[
        GameTable,
        custom_types.Game.id,
        game_schema.GameAdminCreate,
        game_schema.GameAdminUpdate,
        str],
    base.SimpleIdModelService[
        GameTable,
        custom_types.Game.id,
    ]
):
    _MODEL = GameTable

    @classmethod
    async def fetch_many_by_team(cls, session: AsyncSession, team_id: custom_types.Team.id) -> Sequence[GameTable]:
        """returns all games that a given team_id plays in"""

        return await cls.fetch_many(
            session,
            pagination=pagination_schema.Pagination(limit=1000, offset=0),
            query=select(cls._MODEL).where(
                (cls._MODEL.home_team_id == team_id) | (
                    cls._MODEL.away_team_id == team_id)
            )
        )

    @classmethod
    def games_into_game_ids_and_rounds(cls, games: Sequence[GameTable]) -> list[custom_types.GameIdsAndRounds]:

        game_ids_and_rounds: list[custom_types.GameIdsAndRounds] = []
        game_ids_by_round: dict[custom_types.Game.round_id,
                                list[custom_types.Game.id]] = {}

        for game in games:
            if game.round_id not in game_ids_by_round:
                game_ids_by_round[game.round_id] = []
            game_ids_by_round[game.round_id].append(game.id)

        for round_id, game_ids in game_ids_by_round.items():
            game_ids_and_rounds.append(
                {
                    'round': round_id,
                    'game_ids': game_ids
                }
            )
        return game_ids_and_rounds

    @classmethod
    async def fetch_team_unknown_games(cls, session: AsyncSession, team_id: custom_types.Team.id) -> Sequence[GameTable]:

        # find rounds where team is currently not scheduled
        # for each of the unscheduled rounds, if round contains a TBD team, send it back

        # Find all round_ids where the given team_id is not scheduled as home or away

        # find all rounds

        all_rounds = set(await cls.fetch_all_rounds(session))

        rounds_with_team = set(await session.exec(select(col(cls._MODEL.round_id)).where(
            (cls._MODEL.home_team_id == team_id) | (
                cls._MODEL.away_team_id == team_id)
        ).distinct()))

        rounds_without_team = list(all_rounds - rounds_with_team)
        rounds_without_team.sort()

        games = []

        new_id = -1
        for round_id in rounds_without_team:

            game_datetime = (await session.exec(select(
                cls._MODEL.datetime
            ).where(
                cls._MODEL.round_id == round_id,
                (cls._MODEL.home_team_id == None) | (
                    cls._MODEL.away_team_id == None)
            ).order_by(
                col(cls._MODEL.datetime).asc()
            ).limit(1))).one_or_none()

            if game_datetime is not None:
                games.append(
                    GameTable(
                        id=new_id,
                        round_id=round_id,
                        datetime=game_datetime
                    )
                )
                new_id -= 1

        return games

    @classmethod
    async def fetch_many_by_round(cls, session: AsyncSession, round_id: custom_types.RoundId) -> Sequence[GameTable]:
        """returns all Games in a given round_id"""

        return await cls.fetch_many(
            session,
            pagination=pagination_schema.Pagination(limit=1000, offset=0),
            query=select(cls._MODEL).where(cls._MODEL.round_id == round_id)
        )

    @classmethod
    async def fetch_all_rounds(cls, session: AsyncSession) -> Sequence[custom_types.RoundId]:
        return (await session.exec(select(col(cls._MODEL.round_id)).distinct().order_by(col(cls._MODEL.round_id).asc()))).all()

    @classmethod
    async def fetch_game_ids_and_rounds(cls, session: AsyncSession, round_ids: Literal['all'] | list[custom_types.RoundId] = 'all') -> list[custom_types.GameIdsAndRounds]:
        """returns a list of game_ids and round_ids"""

        if round_ids == 'all':
            round_ids = list(await cls.fetch_all_rounds(session))

        game_ids_and_rounds: list[custom_types.GameIdsAndRounds] = []
        for round_id in round_ids:
            game_ids_and_rounds.append(
                {
                    'round': round_id,
                    'game_ids': list((await session.exec(select(col(cls._MODEL.id)).where(cls._MODEL.round_id == round_id))).all())
                }
            )

        return game_ids_and_rounds

    @classmethod
    async def fetch_relevant_rounds(cls, session: AsyncSession) -> list[custom_types.RoundId]:
        """returns two relevant rounds (for the homepage), last round's games and the upcoming games"""

        datetime_now = datetime_module.datetime.now(
            tz=datetime_module.timezone.utc)

        prior_round_id = (await session.exec(select(col(cls._MODEL.round_id)).where(cls._MODEL.datetime < datetime_now).order_by(col(cls._MODEL.datetime).desc()).limit(1))).first()
        next_round_id = (await session.exec(select(col(cls._MODEL.round_id)).where(cls._MODEL.datetime > datetime_now).order_by(col(cls._MODEL.datetime).asc()).limit(1))).first()

        rounds: list[custom_types.RoundId] = []
        if prior_round_id is not None:
            rounds.append(prior_round_id)
        if next_round_id is not None and next_round_id != prior_round_id:
            rounds.append(next_round_id)

        return rounds

    # def assign_teams_to_games(self, session: AsyncSession, n_rounds: int = config.REGULAR_SEASON_ROUNDS):
    #     """randomly assign games for each division"""

    #     from kabbes_matchup_scheduler.scheduler import Scheduler
    #     divisions = division.Divisions.get_real(db)

    #     rounds = []
    #     for i in range(n_rounds):
    #         rounds.append([])

    #     for division_inst in divisions:
    #         division_teams = team.Teams.get_by_division(db, division_inst._id)
    #         division_teams_ids = list(division_teams.d.keys())

    #         scheduler = Scheduler(overwrite_config={
    #             'n_teams': len(division_teams),
    #             'n_rounds': n_rounds,
    #             'teams_per_matchup': 2,
    #             'matchups_per_round': len(division_teams)//2
    #         })
    #         scheduler.run()

    #         for round_index in range(n_rounds):
    #             for matchup_index in range(len(scheduler.schedule[round_index])):
    #                 rounds[round_index].append(
    #                     [division_teams_ids[team_id] for team_id in scheduler.schedule[round_index][matchup_index]])

    #     game_id = 1
    #     for round_index in range(n_rounds):
    #         random.shuffle(rounds[round_index])

    #         for matchup_index in range(len(rounds[round_index])):
    #             self.d[game_id].home_team_id = rounds[round_index][matchup_index][0]
    #             self.d[game_id].away_team_id = rounds[round_index][matchup_index][1]
    #             game_id += 1

    #     self.export_to_db(db)
