from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class TournamentExport(FromAttributes):
    id: custom_types.Tournament.id
    name: custom_types.Tournament.name


class TournamentUpdate(BaseModel):
    name: custom_types.Tournament.name | None = None


class TournamentAdminUpdate(TournamentUpdate):
    pass


class TournamentCreate(BaseModel):
    name: custom_types.Tournament.name


class TournamentAdminCreate(TournamentCreate):
    pass
