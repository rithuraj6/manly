from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import EmailOTP

def send_otp(user, purpose):
    otp = get_random_string(6, allowed_chars="0123456789")

  
    EmailOTP.objects.filter(
        email=user.email,
        purpose=purpose
    ).delete()

    EmailOTP.objects.create(
        email=user.email,
        otp=otp,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    send_mail(
        subject="Your MANLY OTP",
        message=f"Your OTP is {otp}",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )
