import random
from datetime import timedelta
from django.utils import timezone
from .models import EmailOTP

def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(user, purpose="signup"):
    # Invalidate old OTPs
    EmailOTP.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    otp_code = generate_otp()

    EmailOTP.objects.create(
        user=user,
        otp=otp_code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    # DEV ONLY
    print(f"[OTP] {purpose.upper()} OTP for {user.email}: {otp_code}")


def verify_user_otp(user_id, otp_code, purpose):
    try:
        otp = EmailOTP.objects.filter(
            user_id=user_id,
            otp=otp_code,
            purpose=purpose,
            is_used=False
        ).latest("created_at")
    except EmailOTP.DoesNotExist:
        return False

    if otp.is_expired():
        return False

    otp.is_used = True
    otp.save()
    return True
