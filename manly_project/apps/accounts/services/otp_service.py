import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from apps.accounts.models import EmailOTP


OTP_EXPIRY_SECONDS = 75    # 1min 15sec


def generate_otp():
 
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
 
    subject = "MANLY - Verification Code"
    message = (f"Your OTP is {otp}. Expires in 1 minute 15 seconds.")
    
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

def create_or_resend_otp(email):

    otp = generate_otp()
    expires_at = timezone.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={
            "otp": otp,
            "expires_at": expires_at,
        },
    )

    send_otp_email(email, otp)

def verfiy_otp(email,entered_otp):
    
    
    try:
        otp_obj = EmailOTP.objects.get(email=email)
        
    except EmailOTP.DoesNotExist:
        return False, "OTP not found"
    
    if otp_obj.is_expired():
        return False , "invalid OTP"
    if otp_obj.otp != entered_otp :
        return False, "Invalid OTP"
    otp_obj.delete()
    return True , "OTP is Valid"

        
