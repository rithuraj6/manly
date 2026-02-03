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



def name_with_spaces_max10(value: str, field_name="Field"):
    if not value:
        raise ValidationError(f"{field_name} is required")

    value = value.strip()

    if len(value) > 15:
        raise ValidationError(f"{field_name} must not exceed 15 characters")

    if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", value):
        raise ValidationError(
            f"{field_name} must contain only alphabets and spaces"
        )

    return value


def alphabets_only_field(value : str,field_name:str):
    
    if not value:
        raise ValidationError(f"{field_name} is required")
    
    value = value.strip() 
    
    if not value.isalpha():
        raise ValidationError(f"{field_name} must contain only alphabets")
    
    return value

def numbers_only_field(value : str,field_name: str,length=None):
    if not value:
        raise ValidationError(f"{field_name} is  required")
    
    if not value.isdigit():
        raise ValidationError(f"{field_name}must contain only numbers")
    
    if length and len(value) != length:
        raise ValidationError(
            f"{field_name} must be exactly {length} digits"


        )
        
    return value  

 
def validate_phone_number(value : str):
    if not value :
        return ""
    
    value = value.strip()
    
    if not value.isdigit():
        
        raise ValidationError("Phone number must contain only numbers")
    
    if len(value)!=10:
        raise ValidationError("Phone number must be exactly 10")
    
    return value  

def street_field_validator(value :str):
    value = value.strip()
    
    if not value:
        raise ValidationError("Street is required")
    if len(value)<3:
        raise ValidationError("Street is  too short")
    
    if len(value)>225:
        raise ValidationError("Street is too long")
    
    pattern =  r'^[A-Za-z0-9\s,./#-]+$'
    if not re.match(pattern,value):
        raise ValidationError(
            "Street contain invalid characters"
        )
        
    return value



def offer_name_validator(value : str):
    
    if not value:
        raise ValidationError("offer  name is required")
    
   
    
    pattern = r'^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$'
    
    if not re.match(pattern,value):
        raise ValidationError("offer can only contain letter and number!")
    


def coupon_code_validator(value: str):
    if not value:
        raise ValidationError(" coupon is required")
    
   
    
    pattern = r'^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$'
    
    if not re.match(pattern,value):
        raise ValidationError(" coupon name can contain  only letters,numbers, and single  spaces.")