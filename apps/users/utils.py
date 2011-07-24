from users.forms import ProfileForm


def handle_profile_save(request):
    """Edit or create a user profile."""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileForm(data=request.POST,
                           files=request.FILES,
                           instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
        return form
    return ProfileForm(instance=profile)
