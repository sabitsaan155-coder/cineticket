from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_avatar_file_size(file_obj):
    max_size_bytes = 2 * 1024 * 1024
    if file_obj and file_obj.size > max_size_bytes:
        raise ValidationError("Размер аватара не должен превышать 2 MB.")


class Profile(models.Model):
    phone_validator = RegexValidator(
        regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
        message="Введите корректный номер телефона.",
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
                message="Разрешены только файлы JPG, JPEG, PNG и WEBP.",
            ),
            validate_avatar_file_size,
        ],
    )
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True, validators=[phone_validator])

    def __str__(self):
        return f"Profile: {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
