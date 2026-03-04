from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


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
