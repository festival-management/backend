from __future__ import annotations

import typing

from argon2 import PasswordHasher

from backend.config import Config

if typing.TYPE_CHECKING:
    from backend.models.settings import Settings
    from backend.utils.print_manager import PrintManager


class Session:
    config: Config = None
    settings: Settings
    print_manager: PrintManager
    password_hasher: PasswordHasher

    @classmethod
    def set_config(cls) -> None:
        if cls.config is None:
            cls.config = Config()
