from decimal import Decimal

from tortoise import BaseDBAsyncClient

from backend.config import Session
from backend.database.models import (
    Menu,
    MenuField,
    Order,
    OrderMenu,
    OrderMenuField,
    OrderProduct,
    OrderProductIngredient,
    Product,
    Role,
)
from backend.models.orders import (
    CreateOrderMenuItem,
    CreateOrderProductItem,
    CreateOrderMenuFieldItem,
    CreateOrderItem,
)
from backend.services.orders import get_today_quantities
from backend.utils import ErrorCodes

ZERO_DECIMAL = Decimal("0.00")


async def _check_generic_product(
    product_db: Product,
    product: CreateOrderProductItem,
    is_menu: bool = False,
) -> tuple[bool, ErrorCodes | None]:
    # Calculate the base price of the product
    product_price = Decimal(product_db.price).quantize(ZERO_DECIMAL)

    if is_menu:
        product_price = ZERO_DECIMAL

    # Extract variants and their IDs
    product_variants = {variant.id: variant for variant in product_db.variants}

    # Validate variants
    if product_variants and not product.variant_id:
        return (
            True,
            (
                ErrorCodes.INPUT_MENU_FIELD_PRODUCT_VARIANT
                if is_menu
                else ErrorCodes.INPUT_PRODUCT_VARIANT
            ),
        )

    if product.variant_id:
        product_variant = product_variants.get(product.variant_id)
        if not product_variant:
            return (
                True,
                (
                    ErrorCodes.MENU_FIELD_PRODUCT_VARIANT_NOT_EXIST
                    if is_menu
                    else ErrorCodes.PRODUCT_VARIANT_NOT_EXIST
                ),
            )

        if product_variant.is_deleted:
            return (
                True,
                (
                    ErrorCodes.MENU_FIELD_PRODUCT_VARIANT_NOT_EXIST
                    if is_menu
                    else ErrorCodes.PRODUCT_VARIANT_NOT_EXIST
                ),
            )

        product_price += Decimal(product_variant.price).quantize(ZERO_DECIMAL)

    # Extract ingredients and their IDs
    product_ingredients = {
        ingredient.id: ingredient for ingredient in product_db.ingredients
    }

    # Validate ingredients
    if len(set(x.ingredient_id for x in product.ingredients)) != len(
        product.ingredients
    ):
        return (
            True,
            (
                ErrorCodes.INPUT_DUPLICATE_MENU_FIELD_PRODUCT_INGREDIENT
                if is_menu
                else ErrorCodes.INPUT_DUPLICATE_PRODUCT_INGREDIENT
            ),
        )

    for ingredient in product.ingredients:
        product_ingredient = product_ingredients.get(ingredient.ingredient_id)
        if not product_ingredient:
            return (
                True,
                (
                    ErrorCodes.MENU_FIELD_PRODUCT_INGREDIENT_NOT_EXIST
                    if is_menu
                    else ErrorCodes.PRODUCT_INGREDIENT_NOT_EXIST
                ),
            )

        if product_ingredient.is_deleted:
            return (
                True,
                (
                    ErrorCodes.MENU_FIELD_PRODUCT_INGREDIENT_NOT_EXIST
                    if is_menu
                    else ErrorCodes.PRODUCT_INGREDIENT_NOT_EXIST
                ),
            )

        product_price += (Decimal(product_ingredient.price)).quantize(
            ZERO_DECIMAL
        )

    # Assign calculated price to the product
    product._price = product_price
    product._has_cover_charge = product_db.subcategory.include_cover_charge

    return False, None


async def check_products(
    products: list[CreateOrderProductItem],
    role_id: int,
    connection: BaseDBAsyncClient,
) -> tuple[bool, ErrorCodes | None]:
    product_ids = {x.product_id for x in products}  # Extract product IDs

    # Get products from DB
    products_db = (
        Product.filter(id__in=product_ids)
        .prefetch_related(
            "dates", "ingredients", "roles", "variants", "subcategory"
        )
        .using_db(connection)
    )

    # Get today's quantities
    today_quantities = await get_today_quantities(product_ids, connection)

    # Check if all products exist
    total_count = await products_db.count()
    if total_count != len(product_ids):
        return True, ErrorCodes.PRODUCT_NOT_EXIST

    for product in await products_db:
        # Check if role is valid for the product
        if not any(role.role_id == role_id for role in product.roles):
            return True, ErrorCodes.PRODUCT_ROLE_NOT_EXIST

        # Check if any product date is valid
        if not any(
            [await date.is_valid_product_date() for date in product.dates]
        ):
            return True, ErrorCodes.PRODUCT_DATE_NOT_VALID

        # Validate each relevant product in the order
        order_items_for_product = [
            p for p in products if p.product_id == product.id
        ]

        ordered_quantity = sum(x.quantity for x in order_items_for_product)

        if (
            product.daily_max_sales
            and (today_quantities.get(product.id, 0) + ordered_quantity)
            > product.daily_max_sales
        ):
            return True, ErrorCodes.PRODUCT_DAILY_LIMIT_EXCEEDED

        for product_order in order_items_for_product:
            is_invalid, error_code = await _check_generic_product(
                product, product_order
            )

            if is_invalid:
                return is_invalid, error_code

            product_order._price = (
                Decimal(product_order._price) * Decimal(product_order.quantity)
            ).quantize(ZERO_DECIMAL)

    return False, None


async def create_order_products(
    products: list[CreateOrderProductItem],
    order: Order,
    connection: BaseDBAsyncClient,
    order_menu_field: OrderMenuField | None = None,
) -> bool:
    for product in products:
        order_product = await OrderProduct.create(
            product_id=product.product_id,
            price=product._price,
            quantity=product.quantity,
            variant_id=product.variant_id,
            order=order,
            order_menu_field=order_menu_field,
            using_db=connection,
        )

        for ingredient in product.ingredients:
            await OrderProductIngredient.create(
                order_product=order_product,
                product_ingredient_id=ingredient.ingredient_id,
                using_db=connection,
            )

    return True


async def _check_menu_field_products(
    menu_field: MenuField, order_menu_field: CreateOrderMenuFieldItem
) -> tuple[bool, ErrorCodes | None]:
    menu_field_product_ids = {
        product.product_id for product in menu_field.field_products
    }
    order_menu_field_product_ids = {
        product.product_id for product in order_menu_field.products
    }

    # Check for duplicate product IDs in the order
    if len(order_menu_field_product_ids) != len(order_menu_field.products):
        return True, ErrorCodes.DUPLICATE_MENU_FIELDS_PRODUCT

    # Check if all products in the order exist in the menu field
    if not order_menu_field_product_ids.issubset(menu_field_product_ids):
        return True, ErrorCodes.MENU_FIELD_PRODUCT_NOT_EXIST

    can_exceed_max_sortable = menu_field.can_exceed_max_sortable
    max_free_quantity = menu_field.max_sortable_elements
    menu_field_total_quantity = sum(
        p.quantity for p in order_menu_field.products
    )
    excess = menu_field_total_quantity - max_free_quantity

    if (
        not can_exceed_max_sortable
        and menu_field_total_quantity > max_free_quantity
    ):
        return True, ErrorCodes.MENU_FIELD_PRODUCT_QUANTITY_EXCEEDED

    menu_field_product = {
        product.product_id: product for product in menu_field.field_products
    }

    for product in reversed(order_menu_field.products):
        # Validate each product using the generic product checker
        is_invalid, error_code = await _check_generic_product(
            menu_field_product[product.product_id].product, product, True
        )

        if is_invalid:
            return is_invalid, error_code

        # Calculate product price based on quantity
        product._price = (
            Decimal(product._price) * Decimal(product.quantity)
        ).quantize(ZERO_DECIMAL)
        product._price += (
            Decimal(menu_field_product[product.product_id].price)
            * Decimal(product.quantity)
        ).quantize(ZERO_DECIMAL)

        # Apply additional cost for excess quantities
        if excess > 0:
            additional_cost = Decimal(menu_field.additional_cost)

            if product.quantity <= excess:
                product._price += (
                    additional_cost * Decimal(product.quantity)
                ).quantize(ZERO_DECIMAL)
                excess -= product.quantity
            else:
                product._price += (additional_cost * Decimal(excess)).quantize(
                    ZERO_DECIMAL
                )
                excess = 0

    return False, None


async def _check_menu_fields(
    menu: Menu, order_menu: CreateOrderMenuItem
) -> tuple[bool, ErrorCodes | None]:
    menu_field_ids = {field.id for field in menu.menu_fields}
    menu_field_obligatory_ids = {
        field.id for field in menu.menu_fields if not field.is_optional
    }
    order_menu_field_ids = {field.menu_field_id for field in order_menu.fields}

    # Check for duplicate field IDs in the order
    if len(order_menu_field_ids) != len(order_menu.fields):
        return True, ErrorCodes.DUPLICATE_MENU_FIELDS

    # Ensure all obligatory menu fields are present in the order
    if not menu_field_obligatory_ids.issubset(order_menu_field_ids):
        return True, ErrorCodes.MISSING_OBLIGATORY_MENU_FIELDS

    # Validate that all menu fields in the order exist in the menu
    if not order_menu_field_ids.issubset(menu_field_ids):
        return True, ErrorCodes.MENU_FIELD_NOT_EXIST

    menu_fields = {field.id: field for field in menu.menu_fields}
    menu_price = Decimal(menu.price).quantize(ZERO_DECIMAL)

    for field in order_menu.fields:
        # Ensure that each field has at least one product
        if len(field.products) < 1:
            return True, ErrorCodes.MISSING_MENU_FIELD_PRODUCTS

        menu_field = menu_fields[field.menu_field_id]

        # Validate products within the field
        is_invalid, error_code = await _check_menu_field_products(
            menu_field, field
        )

        if is_invalid:
            return is_invalid, error_code

        # Add the price of the products to the menu price
        for product in field.products:
            menu_price += Decimal(product._price).quantize(ZERO_DECIMAL)

    # Assign the calculated menu price to the order
    order_menu._price = Decimal(menu_price).quantize(ZERO_DECIMAL)

    return False, None


async def check_menus(
    menus: list[CreateOrderMenuItem],
    role_id: int,
    connection: BaseDBAsyncClient,
) -> tuple[bool, ErrorCodes | None]:
    menu_ids = {menu.menu_id for menu in menus}

    # Get menus from DB
    menu_db = (
        Menu.filter(id__in=menu_ids)
        .prefetch_related(
            "dates",
            "menu_fields",
            "menu_fields__field_products",
            "menu_fields__field_products__product__subcategory",
            "menu_fields__field_products__product__ingredients",
            "menu_fields__field_products__product__variants",
            "roles",
        )
        .using_db(connection)
    )

    # Get today's quantities
    today_quantities = await get_today_quantities(menu_ids, connection)

    # Check if all products exist
    total_count = await menu_db.count()
    if total_count != len(menu_ids):
        return True, ErrorCodes.MENU_NOT_EXIST

    for menu in await menu_db:
        # Check if role is valid for the product
        if not any(role.role_id == role_id for role in menu.roles):
            return True, ErrorCodes.MENU_ROLE_NOT_EXIST

        # Check if any product date is valid
        if not any([await date.is_valid_menu_date() for date in menu.dates]):
            return True, ErrorCodes.MENU_DATE_NOT_VALID

        # Filter relevant menus for the order
        order_items_for_menu = [m for m in menus if m.menu_id == menu.id]

        ordered_quantity = sum(x.quantity for x in order_items_for_menu)

        if (
            menu.daily_max_sales
            and (today_quantities.get(menu.id, 0) + ordered_quantity)
            > menu.daily_max_sales
        ):
            return True, ErrorCodes.MENU_DAILY_LIMIT_EXCEEDED

        for order_menu in order_items_for_menu:
            # Validate menu fields
            is_invalid, error_code = await _check_menu_fields(menu, order_menu)

            if is_invalid:
                return is_invalid, error_code

            # Calculate the total menu price based on quantity
            order_menu._price = (
                Decimal(order_menu._price) * Decimal(order_menu.quantity)
            ).quantize(ZERO_DECIMAL)

    return False, None


async def create_order_menus(
    menus: list[CreateOrderMenuItem],
    order: Order,
    connection: BaseDBAsyncClient,
) -> bool:
    for menu in menus:
        order_menu = await OrderMenu.create(
            menu_id=menu.menu_id,
            price=menu._price,
            quantity=menu.quantity,
            order=order,
            using_db=connection,
        )

        for field in menu.fields:
            order_menu_field = await OrderMenuField.create(
                order_menu=order_menu,
                menu_field_id=field.menu_field_id,
                using_db=connection,
            )

            await create_order_products(
                field.products, order, connection, order_menu_field
            )

    return True


async def get_order_price(order: CreateOrderItem) -> Decimal:
    cover_change = Decimal(Session.settings.cover_charge)
    guests = Decimal(
        order.guests
        if not order.is_take_away and not order.parent_order_id
        else 0
    )
    price = ZERO_DECIMAL

    include_cover_charge = any(
        order._has_cover_charge for order in order.products
    )
    include_cover_charge |= any(
        product._has_cover_charge
        for menu in order.menus
        for field in menu.fields
        for product in field.products
    )

    if include_cover_charge and not order.is_take_away:
        price = (cover_change * guests).quantize(ZERO_DECIMAL)
    else:
        order.guests = None

    for x in order.products:
        price += Decimal(x._price).quantize(ZERO_DECIMAL)

    for x in order.menus:
        price += Decimal(x._price).quantize(ZERO_DECIMAL)

    return price


async def is_table_allowed_for_role(
    role_id: int,
    table: int,
    connection: BaseDBAsyncClient,
) -> bool:
    role_db = (
        await Role.filter(id=role_id)
        .prefetch_related("tables__table")
        .using_db(connection)
        .first()
    )

    if not role_db:
        return False

    if not role_db.tables:
        return True

    return any(
        t.table.seat_start <= table <= t.table.seat_end for t in role_db.tables
    )
