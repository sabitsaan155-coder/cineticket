from dashboard.permissions import user_is_manager

from .models import Profile


def nav_profile(request):
    if not request.user.is_authenticated:
        return {"nav_profile": None, "nav_is_manager": False}

    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return {
        "nav_profile": profile_obj,
        "nav_is_manager": user_is_manager(request.user),
    }
