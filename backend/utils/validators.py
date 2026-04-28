import ipaddress

from backend.utils.enums import Permission


def validate_username_field(username: str):
    if not username:
        raise ValueError("The `username` field can not be empty")

    if len(username) > 32:
        raise ValueError(
            "The `username` field must have a maximum length of 32 characters"
        )

    if not username.isalpha():
        raise ValueError("The `username` field has illegal characters")

    return username


def validate_password_field(password: str):
    if not password:
        raise ValueError("The `password` field can not be empty")

    if len(password) > 32:
        raise ValueError(
            "The `password` field must have a maximum length of 32 characters"
        )

    return password


def validate_name_field(name: str):
    if not name:
        raise ValueError("The `name` field can not be empty")

    if len(name) > 32:
        raise ValueError(
            "The `name` field must have a maximum length of 32 characters"
        )

    return name


def validate_short_name_field(short_name: str):
    if not short_name:
        raise ValueError("The `short_name` field can not be empty")

    if len(short_name) > 20:
        raise ValueError(
            "The `short_name` field must have a maximum length of 20 characters"
        )

    return short_name


def validate_permissions_field(permissions: dict[Permission, bool]):
    if (
        Permission.CAN_ADMINISTER in permissions
        and permissions[Permission.CAN_ADMINISTER]
    ):
        raise ValueError("The `permissions` field can't be administrators")

    return permissions


def validate_order_field(order: int):
    if order < 0:
        raise ValueError(
            "The `order` field must be greater than or equal to 0"
        )

    return order


def validate_ip_address_field(ip_address: str):
    if not ip_address:
        raise ValueError("The `ip_address` field can not be empty")

    try:
        ipaddress.IPv4Address(ip_address)
        return ip_address
    except ipaddress.AddressValueError:
        raise ValueError(
            "The `ip_address` field can only contain IPv4 addresses"
        )


def validate_receipt_header_field(receipt_header: str):
    if not receipt_header:
        raise ValueError("The `receipt_header` field can not be empty")

    if not all(map(lambda x: len(x) <= 42, receipt_header.split())):
        raise ValueError(
            "The `receipt_header` field can only have line with 42 characters"
        )

    return receipt_header


def check_seat_range(seat_start: int, seat_end: int):
    if seat_start >= seat_end:
        raise ValueError("`seat_start` must be less than `seat_end`")
