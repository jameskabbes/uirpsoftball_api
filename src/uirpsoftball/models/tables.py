from sqlmodel import SQLModel, Field, Relationship, Column
from uirpsoftball.models.custom_field_types import timestamp
from uirpsoftball import custom_types


class Division(SQLModel, table=True):
    __tablename__ = "divisions"  # type: ignore[assignment]

    id: custom_types.Division.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: custom_types.Division.name = Field()

    teams: list["Team"] = Relationship(back_populates="division")


class Location(SQLModel, table=True):
    __tablename__ = "locations"  # type: ignore[assignment]

    id: custom_types.Location.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: custom_types.Location.name = Field()
    link: custom_types.Location.link = Field()
    short_name: custom_types.Location.short_name = Field()
    time_zone: custom_types.Location.time_zone = Field()

    games: list["Game"] = Relationship(back_populates="location")


class Team(SQLModel, table=True):
    __tablename__ = "teams"  # type: ignore[assignment]

    id: custom_types.Team.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: custom_types.Team.name = Field(max_length=256)
    division_id: custom_types.Team.division_id | None = Field(
        foreign_key=str(Division.__tablename__) + '.id', ondelete="SET NULL", nullable=True)
    slug: custom_types.Team.slug = Field(max_length=256)
    seed: custom_types.Team.seed = Field()
    color: custom_types.Team.color | None = Field(
        max_length=6, nullable=True, default=None)

    division: Division = Relationship(
        back_populates="teams")

    home_games: list["Game"] = Relationship(
        back_populates="home_team",
        sa_relationship_kwargs={"foreign_keys": "[Game.home_team_id]"}
    )
    away_games: list["Game"] = Relationship(
        back_populates="away_team",
        sa_relationship_kwargs={"foreign_keys": "[Game.away_team_id]"}
    )
    officiating_games: list["Game"] = Relationship(
        back_populates="officiating_team",
        sa_relationship_kwargs={"foreign_keys": "[Game.officiating_team_id]"}
    )


class Game(SQLModel, table=True):
    __tablename__ = "games"  # type: ignore[assignment]
    id: custom_types.Game.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    round_id: custom_types.Game.round_id = Field()
    home_team_id: custom_types.Game.home_team_id | None = Field(
        foreign_key=str(Team.__tablename__) + '.id', ondelete="SET NULL", nullable=True, default=None)
    away_team_id: custom_types.Game.away_team_id | None = Field(
        foreign_key=str(Team.__tablename__) + '.id', ondelete="SET NULL", nullable=True, default=None)
    officiating_team_id: custom_types.Game.officiating_team_id | None = Field(
        foreign_key=str(Team.__tablename__) + '.id',  ondelete="SET NULL", nullable=True, default=None)
    datetime: custom_types.Game.datetime = Field(
        sa_column=Column(timestamp.Timestamp))
    location_id: custom_types.Game.location_id | None = Field(
        foreign_key=str(Location.__tablename__) + '.id',  ondelete="SET NULL", nullable=True)
    is_accepting_scores: custom_types.Game.is_accepting_scores = Field(
        default=False)
    home_team_score: custom_types.Game.home_team_score | None = Field(
        nullable=True, default=None)
    away_team_score: custom_types.Game.away_team_score | None = Field(
        nullable=True, default=None)

    home_team: Team = Relationship(
        back_populates="home_games",
        sa_relationship_kwargs={"foreign_keys": "[Game.home_team_id]"}
    )
    away_team: Team = Relationship(
        back_populates="away_games",
        sa_relationship_kwargs={"foreign_keys": "[Game.away_team_id]"}
    )
    officiating_team: Team = Relationship(
        back_populates="officiating_games",
        sa_relationship_kwargs={"foreign_keys": "[Game.officiating_team_id]"}
    )
    location: Location = Relationship(back_populates="games")
    tournament_game: "TournamentGame" = Relationship(
        back_populates="game")


class SeedingParameter(SQLModel, table=True):
    __tablename__ = "seeding_parameters"  # type: ignore[assignment]

    id: custom_types.SeedingParameter.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    parameter: custom_types.SeedingParameter.parameter = Field()
    name: custom_types.SeedingParameter.name = Field()


class Tournament(SQLModel, table=True):
    __tablename__ = "tournaments"  # type: ignore[assignment]

    id: custom_types.Tournament.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    name: custom_types.Tournament.name = Field()

    tournament_games: list["TournamentGame"] = Relationship(
        back_populates="tournament")


class TournamentGame(SQLModel, table=True):
    __tablename__ = "tournament_games"  # type: ignore[assignment]

    game_id: custom_types.TournamentGame.game_id = Field(
        primary_key=True, index=True, unique=True, const=True, foreign_key=str(Game.__tablename__) + '.id', ondelete="CASCADE")
    tournament_id: custom_types.TournamentGame.tournament_id = Field(
        foreign_key=str(Tournament.__tablename__) + '.id', ondelete="RESTRICT")
    bracket_id: custom_types.TournamentGame.bracket_id = Field()
    round: custom_types.TournamentGame.round = Field()
    home_team_filler: custom_types.TournamentGame.home_team_filler | None = Field(
        nullable=True, default=None)
    away_team_filler: custom_types.TournamentGame.away_team_filler | None = Field(
        nullable=True, default=None)

    game: Game = Relationship(back_populates="tournament_game")
    tournament: Tournament = Relationship(
        back_populates="tournament_games")


class Visit(SQLModel, table=True):
    __tablename__ = "visits"  # type: ignore[assignment]

    id: custom_types.Visit.id = Field(
        primary_key=True, index=True, unique=True, const=True)
    datetime: custom_types.Visit.datetime = Field(
        sa_column=Column(timestamp.Timestamp))
    path: custom_types.Visit.path = Field()
