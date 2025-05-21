from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import SeedingParameter as SeedingParameterTable
from uirpsoftball.schemas import seeding_parameter as seeding_parameter_schema


class SeedingParameter(
    base.Service[
        SeedingParameterTable,
        custom_types.SeedingParameter.id,
        seeding_parameter_schema.SeedingParameterAdminCreate,
        seeding_parameter_schema.SeedingParameterAdminUpdate,
        str],
    base.SimpleIdModelService[
        SeedingParameterTable,
        custom_types.SeedingParameter.id,
    ]
):
    _MODEL = SeedingParameterTable
