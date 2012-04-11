import cronjobs

from innovate.utils import thumbnailify_image
from users.models import Profile


@cronjobs.register
def resize_profile_avatars():
    """Check all profile avatars and resize those that are too large."""
    for profile in Profile.objects.all():
        thumbnailify_image(profile.avatar)
