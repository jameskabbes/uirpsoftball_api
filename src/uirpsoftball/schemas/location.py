from pydantic import BaseModel
from uirpsoftball import custom_types
from uirpsoftball.schemas import FromAttributes


class LocationExport (FromAttributes):
    id: custom_types.Location.id
    name: custom_types.Location.name
    link: custom_types.Location.link
    short_name: custom_types.Location.short_name
    time_zone: custom_types.Location.time_zone


class LocationUpdate(BaseModel):
    name: custom_types.Location.name | None = None
    link: custom_types.Location.link | None = None
    short_name: custom_types.Location.short_name | None = None
    time_zone: custom_types.Location.time_zone | None = None


class LocationAdminUpdate(LocationUpdate):
    pass


class LocationCreate(BaseModel):
    name: custom_types.Location.name
    link: custom_types.Location.link
    short_name: custom_types.Location.short_name
    time_zone: custom_types.Location.time_zone


class LocationAdminCreate(LocationCreate):
    pass
