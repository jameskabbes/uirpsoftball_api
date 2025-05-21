from fastapi import Depends, status
from sqlmodel import select
from pydantic import BaseModel
from typing import Annotated, cast, Type
from collections.abc import Sequence

from uirpsoftball import config, custom_types
from uirpsoftball.routers import base


class PagesRouter(
    base.Router
):
    _ADMIN = False
    _PREFIX = '/pages'
    _TAG = 'Pages'
