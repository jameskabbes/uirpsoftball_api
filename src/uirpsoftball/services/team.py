from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import Team as TeamTable
from uirpsoftball.schemas import team as team_schema


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
