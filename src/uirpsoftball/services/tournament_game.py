from sqlmodel import select

from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import TournamentGame as TournamentGameTable
from uirpsoftball.schemas import tournament_game as tournament_game_schema


class TournamentGame(
    base.Service[
        TournamentGameTable,
        custom_types.TournamentGame.game_id,
        tournament_game_schema.TournamentGameAdminCreate,
        tournament_game_schema.TournamentGameAdminUpdate,
        str],
):
    _MODEL = TournamentGameTable

    @classmethod
    def model_id(cls, inst):
        return inst.game_id

    @classmethod
    def _build_select_by_id(cls, id):
        return select(cls._MODEL).where(cls._MODEL.game_id == id)
