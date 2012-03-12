import os

from django.conf import settings

import cronjobs
import requests


ISOTOPE_URL = ('https://raw.github.com/desandro/isotope/v1.5.12/'
               'jquery.isotope.min.js')
ISOTOPE_PATH = os.path.join(settings.MEDIA_ROOT, 'js', 'libs',
                            'jquery.isotope.min.js')


@cronjobs.register
def get_isotope():
    """Fetch isotope: https://github.com/desandro/isotope"""
    isotope = requests.get(ISOTOPE_URL)
    with open(ISOTOPE_PATH, 'w') as f:
        f.write(isotope.text)
