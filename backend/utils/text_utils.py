import re
import secrets

from backend.utils.costants import ALPHABET, CAMELCASE_TO_SNAKE_REGEX


def generate_password(length: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def to_snake_case(text: str):
    return re.sub(CAMELCASE_TO_SNAKE_REGEX, "_", text).strip("_")
