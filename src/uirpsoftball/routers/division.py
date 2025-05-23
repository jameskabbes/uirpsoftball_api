from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Division as DivisionTable
from uirpsoftball.services.division import Division as DivisionService
from uirpsoftball.schemas import division as division_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    DivisionTable,
    custom_types.Division.id,
    division_schema.DivisionAdminCreate,
    division_schema.DivisionAdminUpdate,
    str
]):
    _PREFIX = '/divisions'
    _TAG = 'Division'
    _SERVICE = DivisionService


class DivisionRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[division_schema.DivisionExport]:
        return [division_schema.DivisionExport.model_validate(division) for division in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        division_id: custom_types.Division.id,
    ) -> division_schema.DivisionExport:
        return division_schema.DivisionExport.model_validate(
            await cls._get({
                'id': division_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{division_id}/')(self.by_id)
