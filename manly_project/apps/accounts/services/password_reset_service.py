from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail


from  apps.accounts.models import PasswordResetToken



RESET_EXPIRY_MINUTES=15

def send_password_reset_email(user):
    token_obj = PasswordResetToken.objects.create(
        user = user,
        expires_at = timezone.now() + timedelta(minutes= RESET_EXPIRY_MINUTES),
        
    )


    rereset_link = f"http://127.0.0.1:8000/accounts/reset-password/{token_obj.token}/"

    subject = "MANLY - Password Reset"
    message =(
        f"Click the link below to reset your password:\n\n"
        f"{reset_link}\n\n"
        
        
    )
    send_mail(subject, message,None ,[user.email])
    