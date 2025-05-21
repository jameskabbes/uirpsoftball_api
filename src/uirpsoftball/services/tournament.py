from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import Tournament as TournamentTable
from uirpsoftball.schemas import tournament as tournament_schema


class Tournament(
    base.Service[
        TournamentTable,
        custom_types.Tournament.id,
        tournament_schema.TournamentAdminCreate,
        tournament_schema.TournamentAdminUpdate,
        str],
    base.SimpleIdModelService[
        TournamentTable,
        custom_types.Tournament.id,
    ]
):
    _MODEL = TournamentTable
