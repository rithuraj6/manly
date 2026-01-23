from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

only_letters_validator = RegexValidator(
    
    regex =r'^[A-Za-z]+$',
    message = "Only alphabets are allowed."
)


only_numbers_validator = RegexValidator(
    regex=r'^[0-9]+$',
    message='Only numbers are allowed.'
)




def validate_measurement(value, field_name):

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number")

    if value <= 10:
        raise ValidationError(f"{field_name} must be greater than 10")

    if value >= 150:
        raise ValidationError(f"{field_name} must be less than 150")

    return value
