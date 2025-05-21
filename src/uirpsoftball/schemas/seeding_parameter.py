from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class SeedingParameterExport(FromAttributes):
    id: custom_types.SeedingParameter.id
    parameter: custom_types.SeedingParameter.parameter
    name: custom_types.SeedingParameter.name


class SeedingParameterUpdate(BaseModel):
    parameter: custom_types.SeedingParameter.parameter | None = None
    name: custom_types.SeedingParameter.name | None = None


class SeedingParameterAdminUpdate(SeedingParameterUpdate):
    pass


class SeedingParameterCreate(BaseModel):
    parameter: custom_types.SeedingParameter.parameter
    name: custom_types.SeedingParameter.name


class SeedingParameterAdminCreate(SeedingParameterCreate):
    pass
