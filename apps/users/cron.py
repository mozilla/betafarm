import cronjobs
import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User

from django_browserid.auth import default_username_algo

from innovate.utils import thumbnailify_image
from users.models import Profile


logger = logging.getLogger(__name__)


@cronjobs.register
def resize_profile_avatars():
    """Check all profile avatars and resize those that are too large."""
    for profile in Profile.objects.all():
        thumbnailify_image(profile.avatar)


@cronjobs.register
def delete_abandoned_profiles():
    """
    Find and delete users and profiles that never completed their profile,
    and thus never agreed to the privacy policy.
    """
    users = User.objects.filter(
        profile__name='',
        date_joined__lt=datetime.now() - timedelta(days=1),
    )
    for user in users:
        # make sure we don't delete any manually created users
        # e.g. admin
        if user.username == default_username_algo(user.email):
            logger.info('Deleting user %d with email %s', user.id, user.email)
            user.delete()
