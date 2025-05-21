from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class TournamentGameExport(FromAttributes):
    game_id: custom_types.TournamentGame.game_id
    tournament_id: custom_types.TournamentGame.tournament_id | None
    bracket_id: custom_types.TournamentGame.bracket_id
    round: custom_types.TournamentGame.round
    home_team_filler: custom_types.TournamentGame.home_team_filler | None = None
    away_team_filler: custom_types.TournamentGame.away_team_filler | None = None


class TournamentGameUpdate(BaseModel):
    tournament_id: custom_types.TournamentGame.tournament_id | None = None
    bracket_id: custom_types.TournamentGame.bracket_id | None = None
    round: custom_types.TournamentGame.round | None = None
    home_team_filler: custom_types.TournamentGame.home_team_filler | None = None
    away_team_filler: custom_types.TournamentGame.away_team_filler | None = None


class TournamentGameAdminUpdate(TournamentGameUpdate):
    pass


class TournamentGameCreate(BaseModel):
    tournament_id: custom_types.TournamentGame.tournament_id
    bracket_id: custom_types.TournamentGame.bracket_id
    round: custom_types.TournamentGame.round
    home_team_filler: custom_types.TournamentGame.home_team_filler | None = None
    away_team_filler: custom_types.TournamentGame.away_team_filler | None = None


class TournamentGameAdminCreate(TournamentGameCreate):
    pass
