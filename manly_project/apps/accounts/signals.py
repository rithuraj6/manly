from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from django.db.models.signals import post_save
from django.conf import settings

from apps.accounts.models import UserProfile




@receiver(social_account_added)
def mark_google_user(sender, request, sociallogin, **kwargs):
 
    user = sociallogin.user
    user.auth_provider = "google"
    user.save(update_fields=["auth_provider"])

    UserProfile.objects.get_or_create(user=user)

@receiver(social_account_added)
def create_profile_for_google_user(request, sociallogin, **kwargs):
    user = sociallogin.user

    
    user.auth_provider = "google"
    user.save(update_fields=["auth_provider"])

    UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )
User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
