import string


ALPHABET = string.ascii_letters + string.digits
CAMELCASE_TO_SNAKE_REGEX = r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z]"
FMT = (
    "<green>[{time}]</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:"
    "<cyan>{line}</cyan> - <level>{message}</level>"
)
