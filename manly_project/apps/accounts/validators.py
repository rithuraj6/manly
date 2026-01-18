from django.core.validators import RegexValidator

only_letters_validator = RegexValidator(
    
    regex =r'^[A-Za-z]+$',
    message = "Only alphabets are allowed."
)


only_numbers_validator = RegexValidator(
    regex=r'^[0-9]+$',
    message='Only numbers are allowed.'
)