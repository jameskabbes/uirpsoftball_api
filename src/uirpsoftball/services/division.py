from uirpsoftball import custom_types
from uirpsoftball.models.tables import Division as DivisionTable
from uirpsoftball.services import base
from uirpsoftball.schemas import division as division_schema


class Division(
    base.Service[
        DivisionTable,
        custom_types.Division.id,
        division_schema.DivisionAdminCreate,
        division_schema.DivisionAdminUpdate,
        str],
    base.SimpleIdModelService[
        DivisionTable,
        custom_types.Division.id,
    ]
):
    _MODEL = DivisionTable
