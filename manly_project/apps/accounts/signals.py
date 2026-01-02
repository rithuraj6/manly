from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from apps.userprofile.models import UserProfile

@receiver(social_account_added)
def create_profile_for_google_user(request, sociallogin, **kwargs):
    user = sociallogin.user

    UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )
