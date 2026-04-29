from enum import Enum, auto


class ErrorCodes(Enum):
    SUCCESS = 0

    # Auth
    # Login
    INVALID_USERNAME_OR_PASSWORD = auto()
    USERNAME_TOO_LONG = auto()
    # Register
    CANNOT_CREATE_ADMIN_USER = auto()
    USER_ALREADY_EXISTS = auto()

    # Menus
    MENU_ALREADY_EXISTS = auto()
    MENU_NOT_FOUND = auto()
    MENU_SHORT_NAME_ALREADY_EXISTS = auto()
    # Add menu date
    MENU_DATE_ALREADY_EXISTS = auto()
    # Add menu field
    MENU_FIELD_ALREADY_EXISTS = auto()
    # Add menu field product
    MENU_FIELD_PRODUCT_ALREADY_EXISTS = auto()
    # Add menu role
    MENU_ROLE_ALREADY_EXISTS = auto()
    # Delete menu date
    MENU_DATE_NOT_FOUND = auto()
    # Delete menu field
    MENU_FIELD_NOT_FOUND = auto()
    # Delete menu field product
    MENU_FIELD_PRODUCT_NOT_FOUND = auto()
    # Delete menu role
    MENU_ROLE_NOT_FOUND = auto()

    # Orders
    ORDER_NOT_FOUND = auto()
    # Confirm
    ORDER_ALREADY_CONFIRMED = auto()
    # Create
    DUPLICATE_MENU_FIELDS = auto()
    DUPLICATE_MENU_FIELDS_PRODUCT = auto()
    INPUT_MENU_FIELD_PRODUCT_VARIANT = auto()
    INPUT_PRODUCT_VARIANT = auto()
    INPUT_DUPLICATE_PRODUCT_INGREDIENT = auto()
    INPUT_DUPLICATE_MENU_FIELD_PRODUCT_INGREDIENT = auto()
    MENU_DAILY_LIMIT_EXCEEDED = auto()
    MENU_DATE_NOT_VALID = auto()
    MENU_FIELD_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_INGREDIENT_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_VARIANT_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_QUANTITY_EXCEEDED = auto()
    MENU_NOT_EXIST = auto()
    MENU_ROLE_NOT_EXIST = auto()
    MISSING_MENU_FIELD_PRODUCTS = auto()
    MISSING_OBLIGATORY_MENU_FIELDS = auto()
    NO_PRODUCTS_AND_MENUS = auto()
    PRODUCT_DAILY_LIMIT_EXCEEDED = auto()
    PRODUCT_DATE_NOT_VALID = auto()
    PRODUCT_INGREDIENT_NOT_EXIST = auto()
    PRODUCT_NOT_EXIST = auto()
    PRODUCT_ROLE_NOT_EXIST = auto()
    PRODUCT_VARIANT_NOT_EXIST = auto()
    SET_GUESTS_NUMBER = auto()

    # Printers
    PRINTER_NOT_FOUND = auto()
    # Create
    PRINTER_ALREADY_EXISTS = auto()

    # Products
    PRODUCT_ALREADY_EXISTS = auto()
    PRODUCT_NOT_FOUND = auto()
    PRODUCT_SHORT_NAME_ALREADY_EXISTS = auto()
    # Add product date
    PRODUCT_DATE_ALREADY_EXISTS = auto()
    # Add product ingredient
    PRODUCT_INGREDIENT_ALREADY_EXISTS = auto()
    # Add product role
    PRODUCT_ROLE_ALREADY_EXISTS = auto()
    # Add product variant
    PRODUCT_VARIANT_ALREADY_EXISTS = auto()
    # Delete product date
    PRODUCT_DATE_NOT_FOUND = auto()
    # Delete product ingredient
    PRODUCT_INGREDIENT_NOT_FOUND = auto()
    # Delete product role
    PRODUCT_ROLE_NOT_FOUND = auto()
    # Delete product variant
    PRODUCT_VARIANT_NOT_FOUND = auto()

    # Roles
    ROLE_CANNOT_ORDER = auto()
    ROLE_NOT_FOUND = auto()
    # Add role printer
    ROLE_PRINTER_ALREADY_EXISTS = auto()
    # Add role table
    ROLE_TABLE_ALREADY_EXISTS = auto()
    # Create
    ROLE_ALREADY_EXISTS = auto()
    # Delete role printer
    ROLE_PRINTER_NOT_FOUND = auto()
    # Delete role table
    ROLE_TABLE_NOT_FOUND = auto()

    # Subcategories
    SUBCATEGORY_NOT_FOUND = auto()
    # Create
    SUBCATEGORY_ALREADY_EXISTS = auto()

    # Tables
    TABLE_NOT_FOUND = auto()
    # Create
    TABLE_ALREADY_EXISTS = auto()

    # Users
    USER_NOT_FOUND = auto()

    # Token
    INVALID_JWT_TOKEN = auto()

    # Permission
    ADMIN_OPTION_REQUIRED = auto()
    NOT_ALLOWED = auto()
    NOT_AUTHENTICATED = auto()

    # Validation
    DATE_RANGE_INVALID = auto()
    DUPLICATE_DATE = auto()
    ONLY_ONE_STATISTICS_CAN_BE_TRUE = auto()
    PAPER_SIZE_REQUIRED_IF_CAN_ORDER = auto()
    UNKNOWN_ORDER_BY_PARAMETER = auto()
    INVALID_OFFSET_OR_LIMIT_NEGATIVE = auto()

    # Default
    GENERIC_HTTP_EXCEPTION = auto()
    INTERNAL_ERROR_SERVER = auto()
    REQUEST_VALIDATION_ERROR = auto()
