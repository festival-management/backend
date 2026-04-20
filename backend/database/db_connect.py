import re
from functools import partial

from tortoise import connections
from tortoise.contrib.fastapi import RegisterTortoise

from backend.config import Session
from backend.database import models


def is_snake_case(string):
    pattern = r"^[a-z]+(_[a-z]+)*$"
    return bool(re.match(pattern, string))


def init_db():
    conf = Session.config
    config = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": conf.DB_HOST,
                    "port": conf.DB_PORT,
                    "user": conf.DB_USERNAME,
                    "password": conf.DB_PASSWORD,
                    "database": conf.DB_NAME,
                    "minsize": 1,
                    "maxsize": 20,
                },
            }
        },
        "apps": {
            "models": {
                "models": list(
                    map(
                        lambda x: f"backend.database.models.{x}",
                        filter(lambda x: is_snake_case(x), dir(models)),
                    )
                ),
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "Europe/Rome",
    }

    return partial(
        RegisterTortoise,
        config=config,
        generate_schemas=True,
    )


async def stop_db():
    await connections.close_all()
