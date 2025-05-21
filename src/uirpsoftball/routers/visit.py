from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Visit as VisitTable
from uirpsoftball.services.visit import Visit as VisitService
from uirpsoftball.schemas import visit as visit_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    VisitTable,
    custom_types.Visit.id,
    visit_schema.VisitAdminCreate,
    visit_schema.VisitAdminUpdate,
    str
]):
    _PREFIX = '/visits'
    _TAG = 'Visit'
    _SERVICE = VisitService


class VisitRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[visit_schema.VisitExport]:
        return [visit_schema.VisitExport.model_validate(visit) for visit in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        visit_id: custom_types.Visit.id,
    ) -> visit_schema.VisitExport:
        return visit_schema.VisitExport.model_validate(
            await cls._get({
                'id': visit_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{visit_id}')(self.by_id)
