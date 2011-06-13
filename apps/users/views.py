from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from users.forms import RegistrationForm
from users.models import Profile

import jingo


def signin(request):
    return jingo.render(request, 'users/signin.html')


def signup(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            profile = Profile.objects.create_inactive_user(
                form.cleaned_data['username'],
                form.cleaned_data['password'],
                form.cleaned_data['email'],
            )
            profile.send_confirmation_email()
            return jingo.render(request, 'users/signup_done.html')
    return jingo.render(request, 'users/signup.html', dict(form=form))


def confirm(request, confirmation_token):
    profile = get_object_or_404(Profile, confirmation_token=confirmation_token)
    profile.user.is_active = True
    profile.user.save()
    # todo - message about user being activated
    return HttpResponseRedirect(reverse('users_signin'))
