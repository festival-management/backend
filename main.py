import contextlib
import sys

import uvicorn
from argon2 import PasswordHasher
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database import init_db, stop_db
from backend.database.models import Role, User, Setting
from backend.models import BaseResponse, UnicornException
from backend.models.settings import Settings
from backend.utils import ErrorCodes, to_snake_case, generate_password
from backend.utils.costants import FMT
from backend.utils.print_manager import PrintManager

# Logger
logger.remove()

logger.add(sys.stdout, format=FMT)
logger.add(
    "log.log",
    format=FMT,
    rotation="1 day",
    retention="7 days",
)


# Create admin user and role - if not exist
@contextlib.asynccontextmanager
async def lifespan(application: FastAPI):
    # Database - TortoiseORM
    async with init_db()(application):
        logger.info(f"Tortoise-ORM started")

        # Print Manager
        Session.print_manager = await PrintManager.create()
        logger.info("Initializing Print Manager")

        async with in_transaction() as connection:
            # Create settings row
            setting = await Setting.first(using_db=connection)

            if not setting:
                setting = await Setting.create(using_db=connection)

            # Settings
            Session.settings = Settings(**await setting.to_dict())

            # Create admin and base role
            role, _ = await Role.get_or_create(
                name="admin",
                defaults={"can_administer": True},
                using_db=connection,
            )

            await Role.get_or_create(name="base", using_db=connection)

            # Create admin user
            password = generate_password()
            ph = Session.password_hasher = PasswordHasher()
            _, created = await User.get_or_create(
                username="admin",
                defaults={
                    "password": ph.hash(password),
                    "role": role,
                },
                using_db=connection,
            )

        if created:
            logger.info(f"Created the admin user with password {password}")

        yield

        await stop_db()
        logger.info("Tortoise-ORM shutdown")


# Config - Pydantic
Session.set_config()
logger.info("Initializing Config")

# FastAPI - instance
app = FastAPI(title="FestivalBackend", docs_url="/", lifespan=lifespan)
logger.info("Starting FastAPI application")

# CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Setting CORS")

# FastAPI - APIRouter
from backend.api import api

app.include_router(api)
logger.info("Initializing API routers")


# Handling Errors
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(_: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status,
        content=BaseResponse(
            error=True,
            message=exc.message,
            code=exc.code.value
            if exc.code
            else ErrorCodes.GENERIC_HTTP_EXCEPTION.value,
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    error_code: ErrorCodes = getattr(
        ErrorCodes,
        to_snake_case(exc.detail).upper(),
        ErrorCodes.GENERIC_HTTP_EXCEPTION,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            error=True,
            code=error_code.value,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, __: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            error=True, code=ErrorCodes.REQUEST_VALIDATION_ERROR.value
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(_: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content=BaseResponse(
            error=True,
            code=ErrorCodes.INTERNAL_ERROR_SERVER.value,
        ).model_dump(),
    )


if __name__ == "__main__":
    try:
        uvicorn.run(app, host=Session.config.APP_HOST)

    except KeyboardInterrupt:
        pass
