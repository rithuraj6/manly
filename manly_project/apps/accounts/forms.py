from django import forms
from django.contrib.auth import get_user_model
from .validators import only_letters_validator

User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[only_letters_validator],
        max_length=30
    )
    last_name = forms.CharField(
        validators=[only_letters_validator],
        max_length=30
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
