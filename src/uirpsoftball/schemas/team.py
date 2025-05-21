from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class TeamExport(FromAttributes):
    id: custom_types.Team.id
    name: custom_types.Team.name
    division_id: custom_types.Team.division_id | None
    slug: custom_types.Team.slug
    color: custom_types.Team.color | None


class TeamUpdate(BaseModel):
    name: custom_types.Team.name | None = None
    division_id: custom_types.Team.division_id | None = None
    slug: custom_types.Team.slug | None = None
    color: custom_types.Team.color | None = None


class TeamAdminUpdate(TeamUpdate):
    pass


class TeamCreate(BaseModel):
    name: custom_types.Team.name
    division_id: custom_types.Team.division_id
    slug: custom_types.Team.slug
    color: custom_types.Team.color | None = None


class TeamAdminCreate(TeamCreate):
    pass
