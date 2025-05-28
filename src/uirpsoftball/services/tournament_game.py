from sqlmodel import select

from uirpsoftball import custom_types, config
from uirpsoftball.models.tables import TournamentGame as TournamentGameTable
from uirpsoftball.services import base
from uirpsoftball.schemas import tournament_game as tournament_game_schema, pagination as pagination_schema

TournamentGameDetails = dict[custom_types.Tournament.id,
                                      dict[int, dict[custom_types.Game.round_id, list[tournament_game_schema.TournamentGameExport]]]]


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

    @classmethod
    async def get_tournament_game_details(cls):

        async with config.ASYNC_SESSIONMAKER() as session:

            tournament_games = await cls.fetch_many(
                session=session,
                pagination=pagination_schema.Pagination(limit=1000, offset=0),
            )


            d: TournamentGameDetails = {}
            for tournament_game in tournament_games:

                if tournament_game.tournament_id not in d:
                    d[tournament_game.tournament_id] = {}

                if tournament_game.bracket_id not in d[tournament_game.tournament_id]:
                    d[tournament_game.tournament_id][tournament_game.bracket_id] = {
                    }

                if tournament_game.round not in d[tournament_game.tournament_id][tournament_game.bracket_id]:
                    d[tournament_game.tournament_id][tournament_game.bracket_id][tournament_game.round] = [
                    ]

                d[tournament_game.tournament_id][tournament_game.bracket_id][tournament_game.round].append(
                    tournament_game_schema.TournamentGameExport.model_validate(tournament_game))

            return d
