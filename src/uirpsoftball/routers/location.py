from fastapi import Depends, status
from sqlmodel import select
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base
from uirpsoftball.models.tables import Location as LocationTable
from uirpsoftball.services.location import Location as LocationService
from uirpsoftball.schemas import location as location_schema, pagination as pagination_schema, order_by as order_by_schema


class _Base(base.ServiceRouter[
    LocationTable,
    custom_types.Location.id,
    location_schema.LocationAdminCreate,
    location_schema.LocationAdminUpdate,
    str
]):
    _PREFIX = '/locations'
    _TAG = 'Location'
    _SERVICE = LocationService


class LocationRouter(_Base):
    _ADMIN = False

    @classmethod
    async def list(
        cls,
        pagination: Annotated[pagination_schema.Pagination, Depends(
            base.get_pagination())],
    ) -> Sequence[location_schema.LocationExport]:
        return [location_schema.LocationExport.model_validate(location) for location in await cls._get_many({
            'pagination': pagination,
        })]

    @classmethod
    async def by_id(
        cls,
        location_id: custom_types.Location.id,
    ) -> location_schema.LocationExport:
        return location_schema.LocationExport.model_validate(
            await cls._get({
                'id': location_id,
            })
        )

    def _set_routes(self):
        self.router.get('/')(self.list)
        self.router.get('/{location_id}')(self.by_id)
