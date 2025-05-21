from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import Location as LocationTable
from uirpsoftball.schemas import location as location_schema


class Location(
    base.Service[
        LocationTable,
        custom_types.Location.id,
        location_schema.LocationAdminCreate,
        location_schema.LocationAdminUpdate,
        str],
    base.SimpleIdModelService[
        LocationTable,
        custom_types.Location.id,
    ]
):
    _MODEL = LocationTable
