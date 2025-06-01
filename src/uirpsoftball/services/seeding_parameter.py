from typing import ClassVar, Callable

from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import SeedingParameter as SeedingParameterTable
from uirpsoftball.schemas import seeding_parameter as seeding_parameter_schema, team as team_schema

from collections.abc import Sequence


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

    # # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    # ACQUIRE_PARAMETER_VALUES: typing.ClassVar[dict[str, typing.Callable[[list[typing.Any]], list[PARAMETER_VALUE]]]] = {
    #     "win_percentage": lambda standings: SeedingParameter.get_standings_attributes(standings, 'win_percentage'),
    #     "head_to_head": lambda standings: SeedingParameter.head_to_head(standings),
    #     "run_differential": lambda standings: SeedingParameter.get_standings_attributes(standings, 'run_differential'),
    #     # "coin_toss": lambda standings: [random.random() for _ in standings]
    #     "coin_toss": lambda standings: [1 for _ in standings]

    # }

    # @staticmethod
    # def get_standings_attributes(standings, attribute: str) -> list:
    #     return [getattr(standing, attribute) for standing in standings]

    # # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    # def rank_amongst_group(self, standings: typing.Iterable[typing.Any]) -> list[list[typing.Any]]:

    #     values = SeedingParameter.ACQUIRE_PARAMETER_VALUES[self.parameter](
    #         standings)

    #     # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    #     values_and_standings: dict[PARAMETER_VALUE, typing.Any] = {}
    #     for i in range(len(values)):
    #         value = values[i]
    #         standing = standings[i]

    #         if values[i] in values_and_standings:
    #             values_and_standings[value].append(standing)
    #         else:
    #             values_and_standings[value] = [standing]

    #     sorted_unique_values = list(values_and_standings.keys())
    #     sorted_unique_values.sort()
    #     sorted_unique_values.reverse()

    #     return [values_and_standings[key] for key in sorted_unique_values]

    #     # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY

    @staticmethod
    def head_to_head(statistics_by_team_id: dict[custom_types.Team.id, team_schema.TeamStatisticsExport]) -> list[int]:
        """rank the seeding group based on their head to head performance
        for each win they have against the group, +1, for each loss, -1
        """

        game_ids_one_team: set[custom_types.Game.id] = set()
        game_ids_two_teams: set[custom_types.Game.id] = set()
        head_to_head_game_ids_by_team: dict[custom_types.Team.id, set[custom_types.Game.id]] = {
        }

        for team_id in statistics_by_team_id:

            team_statistics = statistics_by_team_id[team_id]

            head_to_head_game_ids_by_team[team_id] = set()
            for game_id in team_statistics.game_ids_won:
                if game_id not in game_ids_one_team:
                    game_ids_one_team.add(game_id)
                else:
                    game_ids_two_teams.add(game_id)

            for game_id in team_statistics.game_ids_lost:
                if game_id not in game_ids_one_team:
                    game_ids_one_team.add(game_id)
                else:
                    game_ids_two_teams.add(game_id)

        for team_id in statistics_by_team_id:
            team_statistics = statistics_by_team_id[team_id]
            head_to_head_game_ids_by_team[team_id] = set(
                team_statistics.game_ids_won | team_statistics.game_ids_lost).intersection(game_ids_two_teams)

        # if there are no games between the teams, then the ranking is invalid
        if len(game_ids_two_teams) == 0:
            return [1 for _ in statistics_by_team_id]

        # if not each team has played each other the same amount of times, then the ranking is invalid
        # 3 games *2 = 6, 3 teams, 2 games per team
        total_games_times_2 = len(game_ids_two_teams)*2
        games_per_team = total_games_times_2 / len(statistics_by_team_id)

        for team_id in statistics_by_team_id:
            if len(head_to_head_game_ids_by_team[team_id]) != games_per_team:
                return [1 for _ in statistics_by_team_id]

        # keep track of the W/L record between the teams
        group_rankings = [0, ] * len(standings)

        for game_id in game_ids_two_teams:
            for i, standing in enumerate(standings):
                if game_id in standing.game_ids_won:
                    group_rankings[i] += 1
                elif game_id in standing.game_ids_lost:
                    group_rankings[i] -= 1

        return group_rankings

    # # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    # ACQUIRE_PARAMETER_VALUES: ClassVar[dict[str, Callable[[list[typing.Any]], list[PARAMETER_VALUE]]]] = {
    #     "win_percentage": lambda standings: SeedingParameter.get_standings_attributes(standings, 'win_percentage'),
    #     "head_to_head": lambda standings: SeedingParameter.head_to_head(standings),
    #     "run_differential": lambda standings: SeedingParameter.get_standings_attributes(standings, 'run_differential'),
    #     # "coin_toss": lambda standings: [random.random() for _ in standings]
    #     "coin_toss": lambda standings: [1 for _ in standings]

    # }

    # @staticmethod
    # def get_standings_attributes(standings, attribute: str) -> list:
    #     return [getattr(standing, attribute) for standing in standings]

    # # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    # def rank_amongst_group(self, standings: typing.Iterable[typing.Any]) -> list[list[typing.Any]]:

    #     values = SeedingParameter.ACQUIRE_PARAMETER_VALUES[self.parameter](
    #         standings)

    #     # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY
    #     values_and_standings: dict[PARAMETER_VALUE, typing.Any] = {}
    #     for i in range(len(values)):
    #         value = values[i]
    #         standing = standings[i]

    #         if values[i] in values_and_standings:
    #             values_and_standings[value].append(standing)
    #         else:
    #             values_and_standings[value] = [standing]

    #     sorted_unique_values = list(values_and_standings.keys())
    #     sorted_unique_values.sort()
    #     sorted_unique_values.reverse()

    #     return [values_and_standings[key] for key in sorted_unique_values]

    #     # NEED TO REFACTOR TO HAVE BETTER TYPE SAFETY

    # @staticmethod
    # def head_to_head(standings: typing.Iterable[typing.Any]) -> list[int]:
    #     """rank the seeding group based on their head to head performance
    #     for each win they have against the group, +1, for each loss, -1
    #     """

    #     game_ids_one_team: set[custom_types.GameID] = set()
    #     game_ids_two_teams: set[custom_types.GameID] = set()
    #     head_to_head_game_ids_by_team: dict[custom_types.TeamID, set[custom_types.GameID]] = {
    #     }

    #     for standing in standings:
    #         head_to_head_game_ids_by_team[standing.team_id] = set()
    #         for game_id in standing.game_ids_won:
    #             if game_id not in game_ids_one_team:
    #                 game_ids_one_team.add(game_id)
    #             else:
    #                 game_ids_two_teams.add(game_id)

    #         for game_id in standing.game_ids_lost:
    #             if game_id not in game_ids_one_team:
    #                 game_ids_one_team.add(game_id)
    #             else:
    #                 game_ids_two_teams.add(game_id)

    #     for standing in standings:
    #         head_to_head_game_ids_by_team[standing.team_id] = set(
    #             standing.game_ids_won | standing.game_ids_lost).intersection(game_ids_two_teams)

    #     # if there are no games between the teams, then the ranking is invalid
    #     if len(game_ids_two_teams) == 0:
    #         return [1 for _ in standings]

    #     # if not each team has played each other the same amount of times, then the ranking is invalid
    #     # 3 games *2 = 6, 3 teams, 2 games per team
    #     total_games_times_2 = len(game_ids_two_teams)*2
    #     games_per_team = total_games_times_2 / len(standings)

    #     for standing in standings:
    #         if len(head_to_head_game_ids_by_team[standing.team_id]) != games_per_team:
    #             return [1 for _ in standings]

    #     # keep track of the W/L record between the teams
    #     group_rankings = [0, ] * len(standings)

    #     for game_id in game_ids_two_teams:
    #         for i, standing in enumerate(standings):
    #             if game_id in standing.game_ids_won:
    #                 group_rankings[i] += 1
    #             elif game_id in standing.game_ids_lost:
    #                 group_rankings[i] -= 1

    #     return group_rankings
