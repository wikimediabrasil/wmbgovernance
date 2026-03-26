from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ProfileForm
from .models import Profile

def index(request):
    context = {}
    return render(request, "accounts/index.html", context)


def login_oauth(request):
    return redirect(reverse('social:begin', kwargs={'backend': 'mediawiki'}))


def logout_oauth(request):
    logout(request)
    return redirect(reverse('accounts:index'))


def login_forbidden(request):
    return render(request, 'accounts/forbidden.html', status=403)

@login_required
def profile(request):
    profile_instance = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('accounts:profile'))
    else:
        form = ProfileForm(instance=profile_instance)
    return render(request, 'accounts/profile.html', {'form': form})