from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class DivisionExport(FromAttributes):
    id: custom_types.Division.id
    name: custom_types.Division.name


class DivisionUpdate(BaseModel):
    name: custom_types.Division.name | None = None


class DivisionAdminUpdate(DivisionUpdate):
    pass


class DivisionCreate(BaseModel):
    name: custom_types.Division.name


class DivisionAdminCreate(DivisionCreate):
    pass
