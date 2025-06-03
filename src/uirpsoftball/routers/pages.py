from fastapi import Depends, status, HTTPException
from sqlmodel import select, col
from pydantic import BaseModel
from typing import Annotated, cast, Type
from collections.abc import Sequence
import datetime as datetime_module

from uirpsoftball import config, custom_types, models

from uirpsoftball.models import tables
from uirpsoftball.routers import base, team as team_router, game as game_router
from uirpsoftball.services import team as team_service, game as game_service, location as location_service, division as division_service, tournament as tournament_service, tournament_game as tournament_game_service, seeding_parameter as seeding_parameter_service
from uirpsoftball.schemas import game as game_schema, team as team_schema, location as location_schema, tournament as tournament_schema, tournament_game as tournament_game_schema, division as division_schema, pagination as pagination_schema, seeding_parameter as seeding_parameter_schema, visit as visit_schema


DivisionExportsById = dict[custom_types.Division.id,
                           division_schema.DivisionExport]
LocationExportsById = dict[custom_types.Location.id,
                           location_schema.LocationExport]
TeamExportsById = dict[custom_types.Team.id, team_schema.TeamExport]
TeamStatisticsExportsByTeamId = dict[custom_types.Team.id,
                                     team_schema.TeamStatisticsExport]
GameExportsById = dict[custom_types.Game.id, game_schema.GameExport]
TournamentExportsById = dict[custom_types.Tournament.id,
                             tournament_schema.TournamentExport]
TournamentGameExportsById = dict[custom_types.TournamentGame.game_id,
                                 tournament_game_schema.TournamentGameExport]
VisitExportsById = dict[custom_types.Visit.id, visit_schema.VisitExport]


class GameResponse(BaseModel):
    game: game_schema.GameExport
    teams: TeamExportsById
    location: location_schema.LocationExport | None
    divisions: DivisionExportsById
    team_statistics: TeamStatisticsExportsByTeamId
    team_ids_ranked_by_division: dict[custom_types.Division.id,
                                      Sequence[custom_types.Team.id]]


class HomeResponse(BaseModel):
    games: GameExportsById
    teams: TeamExportsById
    locations: LocationExportsById
    game_ids_and_rounds: list[custom_types.GameIdsAndRounds]
    divisions: DivisionExportsById
    division_ids_ordered: list[custom_types.Division.id]
    team_statistics: TeamStatisticsExportsByTeamId
    team_ids_ranked_by_division: dict[custom_types.Division.id,
                                      Sequence[custom_types.Team.id]]


class ScheduleResponse(BaseModel):

    games: GameExportsById
    teams: TeamExportsById
    locations: LocationExportsById
    game_ids_and_rounds: list[custom_types.GameIdsAndRounds]
    tournaments: list[tournament_schema.TournamentExport]
    tournament_games: tournament_game_service.TournamentGameDetails


class TeamResponse(BaseModel):

    games: GameExportsById
    teams: TeamExportsById
    locations: LocationExportsById
    games_known_ids: list[custom_types.Game.id]
    games_unknown_ids: list[custom_types.Game.id]
    team_id: custom_types.Team.id
    division: division_schema.DivisionExport
    featured_game_id: custom_types.Game.id | None
    team_statistics: TeamStatisticsExportsByTeamId
    team_ids_ranked: Sequence[custom_types.Team.id]


class StandingsResponse(BaseModel):
    teams: TeamExportsById
    divisions: DivisionExportsById
    division_ids_ordered: Sequence[custom_types.Division.id]
    team_statistics: TeamStatisticsExportsByTeamId
    team_ids_ranked_by_division: dict[custom_types.Division.id,
                                      Sequence[custom_types.Team.id]]
    seeding_parameters: Sequence[seeding_parameter_schema.SeedingParameterExport]


class AdminResponse(BaseModel):
    games: GameExportsById
    teams: TeamExportsById
    locations: LocationExportsById
    game_ids_and_rounds: list[custom_types.GameIdsAndRounds]


class PagesRouter(
    base.Router
):
    _ADMIN = False
    _PREFIX = '/pages'
    _TAG = 'Pages'

    @classmethod
    async def home(cls) -> HomeResponse:

        async with config.ASYNC_SESSIONMAKER() as session:

            relevant_rounds = await game_service.Game.fetch_relevant_rounds(session)
            print(relevant_rounds)
            games = await game_service.Game.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
                query=select(game_service.Game._MODEL).where(
                    col(game_service.Game._MODEL.round_id).in_(relevant_rounds)
                ).order_by(col(game_service.Game._MODEL.datetime).asc(),
                           col(game_service.Game._MODEL.location_id).asc()
                           ))
            teams = await team_service.Team.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            locations = await location_service.Location.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            divisions = await division_service.Division.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )

            return HomeResponse(
                games={game.id: game_schema.GameExport.model_validate(
                    game) for game in games},
                teams={team.id: team_schema.TeamExport.model_validate(
                    team) for team in teams},
                locations={location.id: location_schema.LocationExport.model_validate(
                    location) for location in locations},
                divisions={division.id: division_schema.DivisionExport.model_validate(
                    division) for division in divisions},
                division_ids_ordered=[division.id for division in divisions],
                game_ids_and_rounds=game_service.Game.games_into_game_ids_and_rounds(
                    games),
                team_statistics=await team_service.Team.calculate_statistics(
                    session,
                    team_ids=[team.id for team in teams]
                ),
                team_ids_ranked_by_division={
                    division.id: await team_service.Team.rank_by_division(
                        session,
                        division.id,
                        pagination=pagination_schema.Pagination(
                            limit=1000, offset=0)
                    ) for division in divisions
                }


            )

    @classmethod
    async def team(cls, team_slug: custom_types.Team.slug) -> TeamResponse:

        async with config.ASYNC_SESSIONMAKER() as session:

            team_id = await team_service.Team.id_from_slug(session, team_slug)

            if team_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Team with slug {team_slug} not found',
                )

            games_known: list[tables.Game] = list(await game_service.Game.fetch_many_by_team(session, team_id))
            games_unknown: list[tables.Game] = []
            # games_unknown: list[tables.Game] = list(await game_service.Game.fetch_team_unknown_rounds(session, team_id))

            teams = await team_service.Team.fetch_many(session, pagination=pagination_schema.Pagination(limit=1000, offset=0))

            teams_export = {team.id: team_schema.TeamExport.model_validate(
                team) for team in teams}

            division = await division_service.Division.fetch_one(
                session,
                select(division_service.Division._MODEL).where(
                    division_service.Division._MODEL.id == teams_export[team_id].division_id)
            )

            featured_game_id = None
            if len(games_known) > 0:
                game_id_by_datetimes = {
                    game.datetime: game for game in games_known}
                datetime_now = datetime_module.datetime.now(
                    tz=datetime_module.timezone.utc)

                for datetime in sorted(game_id_by_datetimes.keys()):
                    if datetime > datetime_now:
                        featured_game_id = game_id_by_datetimes[datetime].id
                        break

            return TeamResponse(
                games={game.id: game_schema.GameExport.model_validate(
                    game) for game in games_known},
                locations={location.id: location_schema.LocationExport.model_validate(location) for location in await location_service.Location.fetch_many(session, pagination=pagination_schema.Pagination(limit=1000, offset=0))},
                teams=teams_export,
                games_known_ids=[game.id for game in games_known],
                division=division_schema.DivisionExport.model_validate(
                    division),
                games_unknown_ids=[game.id for game in games_unknown],
                team_id=team_id,
                featured_game_id=featured_game_id,
                team_statistics=await team_service.Team.calculate_statistics(
                    session,
                    team_ids=[team.id for team in teams]
                ),
                team_ids_ranked=[] if division is None else await team_service.Team.rank_by_division(
                    session,
                    division.id,
                    pagination=pagination_schema.Pagination(
                        limit=1000, offset=0
                    )
                )
            )

    @classmethod
    async def schedule(cls) -> ScheduleResponse:
        async with config.ASYNC_SESSIONMAKER() as session:

            games = await game_service.Game.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0))
            teams = await team_service.Team.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            locations = await location_service.Location.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            tournaments = await tournament_service.Tournament.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )

            return ScheduleResponse(
                games={game.id: game_schema.GameExport.model_validate(
                    game) for game in games},
                teams={team.id: team_schema.TeamExport.model_validate(
                    team) for team in teams},
                locations={location.id: location_schema.LocationExport.model_validate(
                    location) for location in locations},
                tournaments=[tournament_schema.TournamentExport.model_validate(
                    tournament) for tournament in tournaments],
                game_ids_and_rounds=game_service.Game.games_into_game_ids_and_rounds(
                    games),
                tournament_games=await tournament_game_service.TournamentGame.get_tournament_game_details(),
            )

    @classmethod
    async def game(cls, game_id: custom_types.Game.id) -> GameResponse:
        async with config.ASYNC_SESSIONMAKER() as session:

            game = await game_router.GameRouter._get({
                'id': game_id,
            })
            teams = await team_service.Team.fetch_many(
                session,
                pagination=pagination_schema.Pagination(
                    limit=1000, offset=0),
            )

            location = None
            if game.location_id is not None:
                location = await location_service.Location.fetch_by_id(
                    session,
                    game.location_id
                )
            home_team = None if game.home_team_id is None else await team_service.Team.fetch_by_id(
                session,
                game.home_team_id
            )
            away_team = None if game.away_team_id is None else await team_service.Team.fetch_by_id(
                session,
                game.away_team_id
            )

            division_ids_ordered = []
            if home_team is not None:
                division_ids_ordered.append(home_team.division_id)
            if away_team is not None:
                division_ids_ordered.append(away_team.division_id)

            divisions = await division_service.Division.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
                query=select(division_service.Division._MODEL).where(
                    col(division_service.Division._MODEL.id).in_(
                        division_ids_ordered
                    )
                )
            )

            return GameResponse(
                game=game_schema.GameExport.model_validate(game),
                teams={team.id: team_schema.TeamExport.model_validate(
                    team) for team in teams},
                location=location_schema.LocationExport.model_validate(
                    location) if location else None,
                divisions={division.id: division_schema.DivisionExport.model_validate(
                    division) for division in divisions},
                team_statistics=await team_service.Team.calculate_statistics(
                    session,
                    team_ids=[team.id for team in teams]
                ),
                team_ids_ranked_by_division={
                    division.id: await team_service.Team.rank_by_division(
                        session,
                        division.id,
                        pagination=pagination_schema.Pagination(
                            limit=1000, offset=0)
                    ) for division in divisions
                }
            )

    @classmethod
    async def standings(cls) -> StandingsResponse:
        async with config.ASYNC_SESSIONMAKER() as session:
            teams = await team_service.Team.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            divisions = await division_service.Division.fetch_many(session, pagination=pagination_schema.Pagination(limit=1000, offset=0))

            return StandingsResponse(
                teams={team.id: team_schema.TeamExport.model_validate(
                    team) for team in teams},
                divisions={division.id: division_schema.DivisionExport.model_validate(
                    division) for division in divisions},
                division_ids_ordered=[
                    division.id for division in divisions
                ],
                team_statistics=await team_service.Team.calculate_statistics(
                    session,
                    team_ids=[team.id for team in teams]
                ),
                team_ids_ranked_by_division={
                    division.id: await team_service.Team.rank_by_division(
                        session,
                        division.id,
                        pagination=pagination_schema.Pagination(
                            limit=1000, offset=0)
                    ) for division in divisions
                },
                seeding_parameters=[seeding_parameter_schema.SeedingParameterExport.model_validate(seeding_parameter) for seeding_parameter in
                                    await seeding_parameter_service.SeedingParameter.fetch_many(
                    session,
                    pagination=pagination_schema.Pagination(
                        limit=1000, offset=0),
                    query=select(seeding_parameter_service.SeedingParameter._MODEL).order_by(
                        col(seeding_parameter_service.SeedingParameter._MODEL.rank).asc()
                    )

                )
                ]
            )

    @classmethod
    async def admin(cls) -> AdminResponse:
        async with config.ASYNC_SESSIONMAKER() as session:

            games = await game_service.Game.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0))
            teams = await team_service.Team.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )
            locations = await location_service.Location.fetch_many(
                session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )

            return AdminResponse(
                games={game.id: game_schema.GameExport.model_validate(
                    game) for game in games},
                teams={team.id: team_schema.TeamExport.model_validate(
                    team) for team in teams},
                locations={location.id: location_schema.LocationExport.model_validate(
                    location) for location in locations},
                game_ids_and_rounds=game_service.Game.games_into_game_ids_and_rounds(
                    games),
            )

    def _set_routes(self):
        self.router.get('/')(self.home)
        self.router.get('/team/{team_slug}/')(self.team)
        self.router.get('/schedule/')(self.schedule)
        self.router.get('/game/{game_id}/')(self.game)
        self.router.get('/standings/')(self.standings)
        self.router.get('/admin/')(self.admin)
