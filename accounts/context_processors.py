from .models import Profile


def nav_profile(request):
    if not request.user.is_authenticated:
        return {"nav_profile": None}

    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    return {"nav_profile": profile_obj}
