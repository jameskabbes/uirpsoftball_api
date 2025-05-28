from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class GameExport(FromAttributes):
    id: custom_types.Game.id
    round_id: custom_types.Game.round_id
    home_team_id: custom_types.Game.home_team_id | None
    away_team_id: custom_types.Game.away_team_id | None
    officiating_team_id: custom_types.Game.officiating_team_id | None
    datetime: custom_types.Game.datetime
    location_id: custom_types.Game.location_id | None
    is_accepting_scores: custom_types.Game.is_accepting_scores
    home_team_score: custom_types.Game.home_team_score | None
    away_team_score: custom_types.Game.away_team_score | None


class ScoreUpdate(BaseModel):
    home_team_score: custom_types.Game.home_team_score | None = None
    away_team_score: custom_types.Game.away_team_score | None = None

class IsAcceptingScoresUpdate(BaseModel):
    is_accepting_scores: custom_types.Game.is_accepting_scores | None = None

class GameUpdate(BaseModel):
    round_id: custom_types.Game.round_id | None = None
    home_team_id: custom_types.Game.home_team_id | None = None
    away_team_id: custom_types.Game.away_team_id | None = None
    officiating_team_id: custom_types.Game.officiating_team_id | None = None
    datetime: custom_types.Game.datetime | None = None
    location_id: custom_types.Game.location_id | None = None
    is_accepting_scores: custom_types.Game.is_accepting_scores | None = None
    home_team_score: custom_types.Game.home_team_score | None = None
    away_team_score: custom_types.Game.away_team_score | None = None


class GameAdminUpdate(GameUpdate):
    pass


class GameCreate(BaseModel):
    round_id: custom_types.Game.round_id
    home_team_id: custom_types.Game.home_team_id
    away_team_id: custom_types.Game.away_team_id
    officiating_team_id: custom_types.Game.officiating_team_id
    datetime: custom_types.Game.datetime
    location_id: custom_types.Game.location_id
    is_accepting_scores: custom_types.Game.is_accepting_scores
    home_team_score: custom_types.Game.home_team_score | None = None
    away_team_score: custom_types.Game.away_team_score | None = None


class GameAdminCreate(GameCreate):
    pass
