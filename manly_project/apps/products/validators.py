from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

MAX_PRODUCT_PRICE = Decimal("10000.00")
MIN_PRODUCT_PRICE = Decimal("1.00")


def validate_product_price(value):
    if value in (None, ""):
        raise ValidationError("Price is required.")

    try:
        price = Decimal(value)
    except InvalidOperation:
        raise ValidationError("Invalid price format.")

    if price < MIN_PRODUCT_PRICE:
        raise ValidationError("Price must be greater than 0.")

    if price > MAX_PRODUCT_PRICE:
        raise ValidationError("Price cannot exceed 10000.")

    return price
