from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import Game as GameTable
from uirpsoftball.schemas import game as game_schema


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
