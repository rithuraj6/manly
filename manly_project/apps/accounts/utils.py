from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from apps.accounts.models import EmailOTP
from django.utils.crypto import get_random_string
from apps.accounts.models import SecurityAuditLog
from allauth.socialaccount.models import SocialAccount



def can_user_change_password(user):
    
    if not user.is_authenticated:
        return False


    if SocialAccount.objects.filter(user=user, provider="google").exists() and not user.has_usable_password():
        return False

    return True



OTP_COOLDOWN_SECONDS = 60
OTP_MAX_PER_WINDOW = 4
OTP_WINDOW_MINUTES = 10


def send_otp(user, purpose, email_override=None):
    email = email_override if email_override else user.email
    now = timezone.now()

    
    last_otp = EmailOTP.objects.filter(
        email=email,
        purpose=purpose
    ).order_by("-created_at").first()

    if last_otp and (now - last_otp.created_at).seconds < OTP_COOLDOWN_SECONDS:
        remaining = OTP_COOLDOWN_SECONDS - (now - last_otp.created_at).seconds
        raise ValueError(f"Please wait {remaining} seconds before requesting OTP again")

    window_start = now - timedelta(minutes=OTP_WINDOW_MINUTES)
    otp_count = EmailOTP.objects.filter(
        email=email,
        purpose=purpose,
        created_at__gte=window_start
    ).count()

    if otp_count >= OTP_MAX_PER_WINDOW:
        raise ValueError("Too many OTP requests. Please try again later")

   
    otp = get_random_string(length=6, allowed_chars="0123456789")

    EmailOTP.objects.create(
        email=email,
        otp=otp,
        purpose=purpose,
        expires_at=now + timedelta(minutes=5)
    )
    SecurityAuditLog.objects.create(
        user=user,
        email=email,
        action="otp_sent",
        ip_address=None  
    )

    send_mail(
        subject="Your OTP Verification",
        message=f"Your OTP is {otp}. It is valid for 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


def can_user_change_password(user):
    
    if not user.is_authenticated:
        return False
    if SocialAccount.objects.filter(user=user,provider="google").exists():
        return False
    
    return True
