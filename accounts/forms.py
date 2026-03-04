from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=True,
        max_length=20,
        label="Номер телефона",
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
                message="Введите корректный номер телефона.",
            )
        ],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "phone_number")

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
        content_type = getattr(avatar, "content_type", "")
        if content_type and content_type.lower() not in allowed_mime_types:
            raise forms.ValidationError("Можно загружать только изображения JPG, PNG или WEBP.")

        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Размер файла должен быть не более 2 MB.")

        return avatar
