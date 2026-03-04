MANAGER_GROUP_NAMES = {"Content Manager"}
STAFF_ROLE_GROUP_NAMES = {"Content Manager", "Moderator"}


def user_is_manager(user):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__in=MANAGER_GROUP_NAMES).exists():
        return True
    return user.has_perm("catalog.change_movie") and user.has_perm("catalog.change_screening")


def user_has_staff_role(user):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=STAFF_ROLE_GROUP_NAMES).exists()
