from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import SeedingParameter as SeedingParameterTable
from uirpsoftball.services.seeding_parameter import SeedingParameter as SeedingParameterService
from uirpsoftball.schemas import seeding_parameter as seeding_parameter_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    SeedingParameterTable,
    custom_types.SeedingParameter.id,
    seeding_parameter_schema.SeedingParameterAdminCreate,
    seeding_parameter_schema.SeedingParameterAdminUpdate,
    str
]):
    _PREFIX = '/seeding-parameters'
    _TAG = 'Seeding Parameter'
    _SERVICE = SeedingParameterService


class SeedingParameterRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[seeding_parameter_schema.SeedingParameterExport]:
        return [seeding_parameter_schema.SeedingParameterExport.model_validate(seeding_parameter) for seeding_parameter in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        seeding_parameter_id: custom_types.SeedingParameter.id,
    ) -> seeding_parameter_schema.SeedingParameterExport:
        return seeding_parameter_schema.SeedingParameterExport.model_validate(
            await cls._get({
                'id': seeding_parameter_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{seeding_parameter_id}')(self.by_id)
