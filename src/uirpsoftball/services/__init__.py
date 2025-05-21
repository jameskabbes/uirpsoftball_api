from typing import TypeVar

from uirpsoftball.services.division import Division
from uirpsoftball.services.game import Game
from uirpsoftball.services.location import Location
from uirpsoftball.services.seeding_parameter import SeedingParameter
from uirpsoftball.services.team import Team
from uirpsoftball.services.tournament import Tournament
from uirpsoftball.services.tournament_game import TournamentGame
from uirpsoftball.services.visit import Visit

Service = Division | Game | Location | SeedingParameter | Team | Tournament | TournamentGame | Visit
TService = TypeVar('TService', bound=Service)
TService_co = TypeVar('TService_co', bound=Service, covariant=True)
TService_contra = TypeVar('TService_contra', bound=Service, contravariant=True)
