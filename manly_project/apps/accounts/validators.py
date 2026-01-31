from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

import re


only_letters_validator = RegexValidator(
    
    regex =r'^[A-Za-z]+$',
    message = "Only alphabets are allowed."
)


only_numbers_validator = RegexValidator(
    regex=r'^[0-9]+$',
    message='Only numbers are allowed.'
)





def name_with_spaces_validator(value: str, field_name="Name"):
 
    if not value:
        return

    pattern = r'^[A-Za-z]+(?: [A-Za-z]+)*$'

    if not re.match(pattern, value):
        raise ValidationError(
            f"{field_name} must contain only alphabets and single spaces"
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


def validate_email_strict(email:str):
    if not email:
        raise ValidationError("Email cannot be empty")
    
    email = email.strip()
    
    if " " in email:
        raise ValidationError("Email must not contain spaces")
    
    email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    
    if not re.match(email_regex,email):
        raise ValidationError("Enter a valid email address")
    
    return email

def validate_password_strict(password:str):
    
    if not  password :
        raise ValidationError("Password cannot be empty")
    
    if " " in password:
        raise ValidationError("Password must not contain spaces")
    
    if len(password)< 6:
        raise ValidationError("Password must be at least 6 characters long")
    if len(password)> 10:
        raise ValidationError("Password must not exceed 10 characters")
    
    if not password.isalnum():
        raise ValidationError(
            "Password can  only contain letters and numbers"
        )
        
    return password