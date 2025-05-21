from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from uirpsoftball import config
from uirpsoftball.routers import division, game, location, pages, seeding_parameter, team, tournament_game, tournament, visit


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('startingup')
    yield
    print('closingdown')

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(division.DivisionRouter().router)
app.include_router(team.TeamRouter().router)
app.include_router(game.GameRouter().router)
app.include_router(location.LocationRouter().router)
app.include_router(seeding_parameter.SeedingParameterRouter().router)
app.include_router(tournament.TournamentRouter().router)
app.include_router(tournament_game.TournamentGameRouter().router)
app.include_router(visit.VisitRouter().router)
app.include_router(pages.PagesRouter().router)
