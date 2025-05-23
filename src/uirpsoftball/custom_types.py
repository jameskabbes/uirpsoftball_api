from pydantic import StringConstraints, conint, confloat
from typing import Annotated, TypeVar, TypedDict
import datetime as datetime_module
from collections.abc import Sequence

DivisionId = int
GameId = int
RoundId = int
TeamId = int
LocationId = int
SeedingParameterId = int
TournamentId = int
VisitId = int

timestamp = float


class Division:
    id = DivisionId
    name = Annotated[str, StringConstraints(min_length=1, max_length=256)]


class Location:
    id = LocationId
    name = Annotated[str, StringConstraints(min_length=1, max_length=256)]
    link = Annotated[str, StringConstraints(min_length=1, max_length=1024)]
    short_name = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    time_zone = Annotated[str, StringConstraints(min_length=1, max_length=256)]


_hex_color = Annotated[str, StringConstraints(
    min_length=1, max_length=6)]  # Hex color code without the leading '#'

_seed = conint(ge=1)
_percentage = confloat(ge=0, le=1)


class Team:
    id = TeamId
    name = Annotated[str, StringConstraints(min_length=1, max_length=256)]
    division_id = DivisionId
    slug = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    color = _hex_color
    seed = _seed
    win_percentage = _percentage
    game_ids_won = list[GameId]
    game_ids_lost = list[GameId]


_score = conint(ge=0)


class Game:
    id = GameId
    round_id = RoundId
    home_team_id = TeamId
    away_team_id = TeamId
    officiating_team_id = TeamId
    datetime = datetime_module.datetime
    location_id = LocationId
    is_accepting_scores = bool
    home_team_score = _score
    away_team_score = _score


class SeedingParameter:
    id = SeedingParameterId
    parameter = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]
    name = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]


class Tournament:
    id = TournamentId
    name = Annotated[str, StringConstraints(
        min_length=1, max_length=256)]


class TournamentGame:
    game_id = GameId
    tournament_id = TournamentId
    bracket_id = int
    round = int
    home_team_filler = str
    away_team_filler = str


class Visit:
    id = VisitId
    datetime = datetime_module.datetime
    path = str


SimpleId = DivisionId | GameId | RoundId | TeamId | LocationId | SeedingParameterId | TournamentId | VisitId
Id = SimpleId

TSimpleId = TypeVar('TSimpleId', bound=SimpleId)
TSimpleId_co = TypeVar('TSimpleId_co', bound=SimpleId, covariant=True)
TSimpleId_contra = TypeVar(
    'TSimpleId_contra', bound=SimpleId, contravariant=True)

TId = TypeVar('TId', bound=Id)
TId_co = TypeVar('TId_co', bound=Id, covariant=True)
TId_contra = TypeVar('TId_contra', bound=Id, contravariant=True)


class GameIdsAndRounds(TypedDict):
    round: RoundId
    game_ids: Sequence[GameId]
