from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class VisitExport(FromAttributes):
    id: custom_types.Visit.id
    datetime: custom_types.Visit.datetime
    path: custom_types.Visit.path


class VisitUpdate(BaseModel):
    pass


class VisitAdminUpdate(VisitUpdate):
    pass


class VisitCreate(BaseModel):
    datetime: custom_types.Visit.datetime
    path: custom_types.Visit.path


class VisitAdminCreate(VisitCreate):
    pass
