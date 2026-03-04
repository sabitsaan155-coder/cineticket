from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import m2m_changed, post_migrate
from django.dispatch import receiver

from dashboard.permissions import STAFF_ROLE_GROUP_NAMES


@receiver(post_migrate)
def setup_catalog_groups(sender, **kwargs):
    if sender.name != "catalog":
        return

    content_manager, _ = Group.objects.get_or_create(name="Content Manager")
    moderator, _ = Group.objects.get_or_create(name="Moderator")

    manager_models = [
        "movie",
        "screening",
        "cinema",
        "hall",
        "genre",
        "person",
        "studio",
        "ticketprice",
        "ticketcategory",
    ]
    moderator_models = ["movie", "screening", "genre", "ticketprice"]

    manager_codenames = []
    for model_name in manager_models:
        manager_codenames.extend(
            [
                f"view_{model_name}",
                f"add_{model_name}",
                f"change_{model_name}",
                f"delete_{model_name}",
            ]
        )

    moderator_codenames = []
    for model_name in moderator_models:
        moderator_codenames.extend(
            [
                f"view_{model_name}",
                f"change_{model_name}",
            ]
        )

    manager_permissions = Permission.objects.filter(
        content_type__app_label="catalog",
        codename__in=manager_codenames,
    )
    moderator_permissions = Permission.objects.filter(
        content_type__app_label="catalog",
        codename__in=moderator_codenames,
    )

    content_manager.permissions.set(manager_permissions)
    moderator.permissions.set(moderator_permissions)


User = get_user_model()


@receiver(m2m_changed, sender=User.groups.through)
def sync_staff_flag_with_groups(sender, instance, action, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    if instance.is_superuser:
        return

    should_be_staff = instance.groups.filter(name__in=STAFF_ROLE_GROUP_NAMES).exists()
    if instance.is_staff != should_be_staff:
        instance.is_staff = should_be_staff
        instance.save(update_fields=["is_staff"])
