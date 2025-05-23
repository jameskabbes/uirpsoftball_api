import typer
import asyncio
import json
from sqlmodel import SQLModel
import uvicorn
from uirpsoftball import models, config
from uirpsoftball.app import app as fastapi_app
from uirpsoftball.services import game as game_service

cli = typer.Typer()


@cli.command()
def runserver():
    uvicorn.run("uirpsoftball.app:app", **config.UVICORN)


@cli.command()
def create_tables():
    """Create all database tables."""
    async def _main():
        async with config.DB_ASYNC_ENGINE.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    print("Creating tables...")
    asyncio.run(_main())


@cli.command()
def export_openapi():
    """Export OpenAPI schema to file."""

    print('Exporting OpenAPI schema...')
    config.OPENAPI_SCHEMA_PATH.write_text(json.dumps(fastapi_app.openapi()))


@cli.command()
def test():

    async def _main():
        async with config.ASYNC_SESSIONMAKER() as session:
            print()

    asyncio.run(_main())


if __name__ == "__main__":
    cli()
