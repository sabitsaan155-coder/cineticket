from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ProfileForm, SignUpForm
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile_obj, _ = Profile.objects.get_or_create(user=user)
            profile_obj.phone_number = form.cleaned_data['phone_number']
            profile_obj.save(update_fields=['phone_number'])
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')

            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('core:home')
    else:
        form = SignUpForm()

    return render(request, 'accounts/register.html', {'form': form, 'next': request.GET.get('next', '')})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj)

    return render(request, 'accounts/profile.html', {'form': form})
