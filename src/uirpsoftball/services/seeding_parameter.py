from typing import ClassVar, Callable
from sqlmodel.ext.asyncio.session import AsyncSession

from uirpsoftball import custom_types
from uirpsoftball.services import base
from uirpsoftball.models.tables import SeedingParameter as SeedingParameterTable, Team as TeamTable
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

    @classmethod
    def rank_by_seeding_parameter(cls, session: AsyncSession, seeding_parameter: SeedingParameterTable, teams_by_id: dict[custom_types.Team.id, TeamTable], team_statistics_by_team_id: dict[custom_types.Team.id, team_schema.TeamStatisticsExport]):

        highest_to_lowest_movers = []
        if seeding_parameter.parameter == 'win_percentage':
            highest_to_lowest_movers = cls.win_percentage(
                teams_by_id, team_statistics_by_team_id)
        elif seeding_parameter.parameter == 'head_to_head':
            highest_to_lowest_movers = cls.head_to_head(
                teams_by_id, team_statistics_by_team_id)
        elif seeding_parameter.parameter == 'run_differential':
            highest_to_lowest_movers = cls.run_differential(
                teams_by_id, team_statistics_by_team_id)

        seeds_to_add = 0
        for i in range(len(highest_to_lowest_movers)):
            for team_id in highest_to_lowest_movers[i]:
                teams_by_id[team_id].seed += seeds_to_add
            seeds_to_add += len(highest_to_lowest_movers[i])

    @classmethod
    def win_percentage(cls, teams_by_id: dict[custom_types.Team.id, TeamTable], team_statistics_by_team_id: dict[custom_types.Team.id, team_schema.TeamStatisticsExport]) -> list[set[custom_types.Team.id]]:
        """rank the seeding group based on their win percentage
        win percentage = wins / (wins + losses)
        """

        team_ids_by_win_percentage: dict[custom_types.Team.win_percentage, set[custom_types.Team.id]
                                         ] = {}

        for team_id in teams_by_id:
            team_statistics = team_statistics_by_team_id[team_id]
            win_percentage = 0.0
            if len(team_statistics.game_ids_won) + len(team_statistics.game_ids_lost) > 0:
                win_percentage = len(team_statistics.game_ids_won) / \
                    (len(team_statistics.game_ids_won) +
                     len(team_statistics.game_ids_lost))

            win_percentage = round(win_percentage, 6)
            if win_percentage not in team_ids_by_win_percentage:
                team_ids_by_win_percentage[win_percentage] = set()
            team_ids_by_win_percentage[win_percentage].add(team_id)

        sorted_win_percentages = sorted(
            team_ids_by_win_percentage.keys(), reverse=True)

        return [team_ids_by_win_percentage[win_percentage] for win_percentage in sorted_win_percentages]

    @classmethod
    def run_differential(cls, teams_by_id: dict[custom_types.Team.id, TeamTable], team_statistics_by_team_id: dict[custom_types.Team.id, team_schema.TeamStatisticsExport]) -> list[set[custom_types.Team.id]]:
        """rank the seeding group based on their run differential
        run differential = runs scored - runs allowed
        """

        team_ids_by_run_differential: dict[int, set[custom_types.Team.id]] = {}

        for team_id in teams_by_id:
            team_statistics = team_statistics_by_team_id[team_id]
            run_differential = team_statistics.run_differential

            if run_differential not in team_ids_by_run_differential:
                team_ids_by_run_differential[run_differential] = set()
            team_ids_by_run_differential[run_differential].add(team_id)

        sorted_run_differentials = sorted(
            team_ids_by_run_differential.keys(), reverse=True)

        return [team_ids_by_run_differential[run_differential] for run_differential in sorted_run_differentials]

    @classmethod
    def head_to_head(cls, teams_by_id: dict[custom_types.Team.id, TeamTable], team_statistics_by_team_id: dict[custom_types.Team.id, team_schema.TeamStatisticsExport]) -> list[set[custom_types.Team.id]]:
        """rank the seeding group based on their head to head performance
        for each win they have against the group, +1, for each loss, -1
        """

        game_ids_one_team: set[custom_types.Game.id] = set()
        game_ids_two_teams: set[custom_types.Game.id] = set()
        head_to_head_game_ids_by_team: dict[custom_types.Team.id, set[custom_types.Game.id]] = {
        }

        for team_id in team_statistics_by_team_id:

            team_statistics = team_statistics_by_team_id[team_id]

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

        for team_id in team_statistics_by_team_id:
            team_statistics = team_statistics_by_team_id[team_id]
            head_to_head_game_ids_by_team[team_id] = set(
                team_statistics.game_ids_won | team_statistics.game_ids_lost).intersection(game_ids_two_teams)

        # if there are no games between the teams, then the ranking is invalid
        if len(game_ids_two_teams) == 0:
            return [set(teams_by_id.keys())]

        # if not each team has played each other the same amount of times, then the ranking is invalid
        # 3 games *2 = 6, 3 teams, 2 games per team
        total_games_times_2 = len(game_ids_two_teams)*2
        games_per_team = total_games_times_2 / len(team_statistics_by_team_id)

        for team_id in team_statistics_by_team_id:
            if len(head_to_head_game_ids_by_team[team_id]) != games_per_team:
                return [set(teams_by_id.keys())]

        # keep track of the W/L record between the
        group_rankings_by_team_id: dict[custom_types.Team.id, int] = {
            team_id: 0 for team_id in team_statistics_by_team_id}

        for game_id in game_ids_two_teams:
            for team_id in teams_by_id:
                if game_id in team_statistics_by_team_id[team_id].game_ids_won:
                    group_rankings_by_team_id[team_id] += 1
                elif game_id in team_statistics_by_team_id[team_id].game_ids_lost:
                    group_rankings_by_team_id[team_id] -= 1

        # now, sort by the head to head record and apply the rankings

        team_ids_by_group_rankings: dict[int, set[custom_types.Team.id]] = {}
        for team_id, group_ranking in group_rankings_by_team_id.items():
            if group_ranking not in team_ids_by_group_rankings:
                team_ids_by_group_rankings[group_ranking] = set()
            team_ids_by_group_rankings[group_ranking].add(team_id)

        sorted_group_rankings = sorted(
            team_ids_by_group_rankings.keys(), reverse=True)

        return [team_ids_by_group_rankings[group_ranking] for group_ranking in sorted_group_rankings]
