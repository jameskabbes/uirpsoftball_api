from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import Visit as VisitTable
from uirpsoftball.schemas import visit as visit_schema


class Visit(
    base.Service[
        VisitTable,
        custom_types.Visit.id,
        visit_schema.VisitAdminCreate,
        visit_schema.VisitAdminUpdate,
        str],
    base.SimpleIdModelService[
        VisitTable,
        custom_types.Visit.id,
    ]
):
    _MODEL = VisitTable
