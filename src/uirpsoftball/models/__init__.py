from uirpsoftball import custom_types
from uirpsoftball.models import tables
from typing import TypeVar, Generic, Protocol

ModelSimple = tables.Division | tables.Location | tables.Team | tables.Game | tables.SeedingParameter | tables.Tournament | tables.Visit
Model = ModelSimple | tables.TournamentGame

TModel = TypeVar('TModel', bound=Model)
TModel_co = TypeVar('TModel_co', bound=Model, covariant=True)
TModel_contra = TypeVar('TModel_contra', bound=Model, contravariant=True)

TSimpleModel = TypeVar('TSimpleModel', bound=ModelSimple)
TSimpleModel_co = TypeVar('TSimpleModel_co', bound=ModelSimple, covariant=True)
TSimpleModel_contra = TypeVar(
    'TSimpleModel_contra', bound=ModelSimple, contravariant=True)


class HasSimpleId(Generic[custom_types.TSimpleId], Protocol):
    id: custom_types.TSimpleId
