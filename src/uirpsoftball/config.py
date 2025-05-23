from sqlmodel.ext.asyncio.session import AsyncSession as SQLMAsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
import json
from pathlib import Path
import os
import typing
from typing import TypedDict, NotRequired, Literal
import yaml
from dotenv import dotenv_values
import datetime as datetime_module
import isodate
from platformdirs import user_config_dir
import warnings
import secrets
from uirpsoftball import custom_types
import toml

UIRPSOFTBALL_DIR = Path(__file__).parent
SRC_DIR = UIRPSOFTBALL_DIR.parent
REPO_DIR = SRC_DIR.parent

EXAMPLES_DIR = UIRPSOFTBALL_DIR / "examples"
EXAMPLES_CONFIG_DIR = EXAMPLES_DIR / "config"

EXAMPLE_BACKEND_CONFIG_PATH = EXAMPLES_CONFIG_DIR / "backend.yaml"
EXAMPLE_SHARED_CONFIG_PATH = EXAMPLES_CONFIG_DIR / "shared.yaml"

PYPROJECT_TOML_PATH = REPO_DIR / "pyproject.toml"

PYPROJECT_TOML_CONTENT = toml.load(PYPROJECT_TOML_PATH)

# POSSIBLE ENVIRONMENT VARIABLES

# Priority 1. These three paths are explicit paths set to config files
_backend_config_path = os.getenv('BACKEND_CONFIG_PATH', None)
_shared_config_path = os.getenv('SHARED_CONFIG_PATH', None)

# also included is 'FRONTEND_CONFIG_PATH', which is not used in the backend

# Priority 2. This specifies the config directory, names of config files are fixed
_config_env_dir = os.getenv('CONFIG_ENV_DIR', None)

# Priority 3. This specifies the name of the config folder, parent direct is the user config dir
_app_env = os.getenv('APP_ENV', None)


def convert_env_path_to_absolute(root_dir: Path, a: str) -> Path:
    """process a relative path sent to an environment variable"""
    A = Path(a)
    if A.is_absolute():
        return A
    else:
        return (root_dir / A).resolve()


def process_explicit_config_path(config_path: str | None) -> Path | None:
    """process an explicit config path sent to an environment variable"""

    if config_path is None:
        return None
    else:
        path = convert_env_path_to_absolute(Path.cwd(), config_path)

        # if the user specifies an exist path, we need to ensure it exists. Do NOT generate a new one
        if not path.exists():
            raise FileNotFoundError(
                'Config path {} does not exist. Please create it or specify a different one.'.format(path))

        return path


BACKEND_CONFIG_PATH = process_explicit_config_path(_backend_config_path)
SHARED_CONFIG_PATH = process_explicit_config_path(_shared_config_path)

if BACKEND_CONFIG_PATH is None or SHARED_CONFIG_PATH is None:

    if _config_env_dir is not None:
        CONFIG_ENV_DIR = convert_env_path_to_absolute(
            Path.cwd(), _config_env_dir)
    else:
        # this is going to reference the USER_CONFIG_DIR
        USER_CONFIG_DIR = Path(user_config_dir(
            PYPROJECT_TOML_CONTENT['project']['name'], appauthor=False))

        if not USER_CONFIG_DIR.exists():
            warnings.warn(
                'Config dir {} does not exist. Creating a new one.'.format(USER_CONFIG_DIR))
            USER_CONFIG_DIR.mkdir()

        if _app_env is not None:
            CONFIG_ENV_DIR = USER_CONFIG_DIR / _app_env
        else:
            CONFIG_ENV_DIR = USER_CONFIG_DIR / 'dev'
            warnings.warn(
                'Environment variables APP_ENV and CONFIG_ENV_DIR are not set. Defaulting to builtin dev environment located at {}.'.format(CONFIG_ENV_DIR))

    if not CONFIG_ENV_DIR.exists():
        CONFIG_ENV_DIR.mkdir()
        warnings.warn(
            'Config env dir {} does not exist. Creating a new one.'.format(CONFIG_ENV_DIR))

    if BACKEND_CONFIG_PATH is None:
        BACKEND_CONFIG_PATH = CONFIG_ENV_DIR / EXAMPLE_BACKEND_CONFIG_PATH.name
        if not BACKEND_CONFIG_PATH.exists():
            warnings.warn(
                'Backend config file {} does not exist. Creating a new one.'.format(BACKEND_CONFIG_PATH))
            BACKEND_CONFIG_PATH.write_text(
                EXAMPLE_BACKEND_CONFIG_PATH.read_text())

    if SHARED_CONFIG_PATH is None:
        SHARED_CONFIG_PATH = CONFIG_ENV_DIR / EXAMPLE_SHARED_CONFIG_PATH.name
        if not SHARED_CONFIG_PATH.exists():
            warnings.warn(
                'Shared config file {} does not exist. Creating a new one.'.format(SHARED_CONFIG_PATH))
            SHARED_CONFIG_PATH.write_text(
                EXAMPLE_SHARED_CONFIG_PATH.read_text())

# Shared config


class SharedConfig(TypedDict):
    BACKEND_URL: str
    FRONTEND_URL: str


with SHARED_CONFIG_PATH.open('r') as f:
    _SHARED_CONFIG: SharedConfig = yaml.safe_load(f)

BACKEND_URL = _SHARED_CONFIG['BACKEND_URL']
FRONTEND_URL = _SHARED_CONFIG['FRONTEND_URL']


class DbEnv(TypedDict):
    URL: str


class BackendConfig(TypedDict):
    DB: DbEnv
    UVICORN: dict
    OPENAPI_SCHEMA_PATH: str
    REGULAR_SEASON_ROUNDS: int
    PLAYOFF_ROUNDS: int
    GAME_TIMEDELTA: str

with BACKEND_CONFIG_PATH.open('r') as f:
    _BACKEND_CONFIG: BackendConfig = yaml.safe_load(f)

DB_ASYNC_ENGINE = create_async_engine(_BACKEND_CONFIG['DB']['URL'])
ASYNC_SESSIONMAKER = async_sessionmaker(
    bind=DB_ASYNC_ENGINE,
    class_=SQLMAsyncSession,
    expire_on_commit=False
)
UVICORN = _BACKEND_CONFIG['UVICORN']

OPENAPI_SCHEMA_PATH = convert_env_path_to_absolute(
    Path.cwd(), _BACKEND_CONFIG['OPENAPI_SCHEMA_PATH'])

REGULAR_SEASON_ROUNDS = _BACKEND_CONFIG['REGULAR_SEASON_ROUNDS']
PLAYOFF_ROUNDS = _BACKEND_CONFIG['PLAYOFF_ROUNDS']
GAME_TIMEDELTA: datetime_module.timedelta = isodate.parse_duration(
    _BACKEND_CONFIG['GAME_TIMEDELTA'])