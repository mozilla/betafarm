# Django settings file for a project based on the playdoh template.

import os

from django.utils.functional import lazy

# Make file paths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

ROOT_PACKAGE = os.path.basename(ROOT)


DEBUG = TEMPLATE_DEBUG = False

ADMINS = ()
MANAGERS = ADMINS

## Internationalization.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Gettext text domain
TEXT_DOMAIN = 'messages'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

# Accepted locales
KNOWN_LANGUAGES = ('en-US',)

# List of RTL locales known to this project. Subset of LANGUAGES.
RTL_LANGUAGES = ()  # ('ar', 'fa', 'fa-IR', 'he')

LANGUAGE_URL_MAP = dict([(i.lower(), i) for i in KNOWN_LANGUAGES])

# Override Django's built-in with our native names
class LazyLangs(dict):
    def __new__(self):
        from product_details import product_details
        return dict([(lang.lower(), product_details.languages[lang]['native'])
                     for lang in KNOWN_LANGUAGES])

# Where to store product details etc.
PROD_DETAILS_DIR = path('lib/product_details_json')

LANGUAGES = lazy(LazyLangs, dict)()

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'push', 'selectable']


## Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'funfactory.context_processors.i18n',
    'funfactory.context_processors.globals',

    #'jingo_minify.helpers.build_ids',

    'topics.context_processors.topics',
    'django.core.context_processors.request',
    'django_browserid.context_processors.browserid_form',
)

TEMPLATE_DIRS = (
    path('templates'),
)

def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
#    from caching.base import cache
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
#    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
#        bc = jinja2.MemcachedBytecodeCache(cache._cache,
#                                           "%sj2:" % settings.CACHE_PREFIX)
#        config['cache_size'] = -1 # Never clear the cache
#        config['bytecode_cache'] = bc
    return config

JINGO_EXCLUDE_APPS = (
    'debug_toolbar',
    'admin',
)

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/main.less',
        ),
        'search': (
            'css/google-search.css',
        ),
        'selectable': (
            'css/jquery-ui-1.8.19.custom.css',
            'selectable/css/dj.selectable.css',
        ),
    },
    'js': {
        'common': (
            'js/libs/jquery-1.6.1.min.js',
            'js/libs/jquery.isotope.min.js',
            'js/functions.js',
        ),
        'search': (
            'js/google-search.js',
        ),
        'selectable': (
            'js/libs/jquery-ui-1.8.19.custom.min.js',
            'selectable/js/jquery.dj.selectable.js',
        ),
    },
}

# Dynamically process LESS server-side? (usually true to local
# development)
LESS_PREPROCESS = False
LESS_BIN = 'lessc'

## Middlewares, apps, URL configs.

MIDDLEWARE_CLASSES = (
    'commons.middleware.LocaleURLMiddleware',
    'commonware.response.middleware.StrictTransportMiddleware',
    'csp.middleware.CSPMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'commonware.middleware.FrameOptionsHeader',
    'innovate.middleware.ProfileMiddleware',

    'waffle.middleware.WaffleMiddleware',
)

ROOT_URLCONF = '%s.urls' % ROOT_PACKAGE

INSTALLED_APPS = (
    # Local apps
    'commons',  # Content common to most playdoh-based apps.
    'jingo_minify',
    'tower',  # for ./manage.py extract (L10n)

    # We need this so the jsi18n view will pick up our locale directory.
    ROOT_PACKAGE,

    # Third-party apps
    'commonware.response.cookies',
    'djcelery',

    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django_sha2',  # Load after auth to monkey-patch it.

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # L10n
    'product_details',

    # Database migrations
    'south',

    # Gooder tests. Has to come after south.
    'django_nose',

    # CSP
    'csp',

    # BrowserID support
    'django_browserid',

    # Tagging
    'taggit',

    # Feed subscription
    'django_push.subscriber',
    'feeds',

    # Feature flipping
    'waffle',

    # Command running
    'cronjobs',

    # Autocomplete
    'selectable',

    # Betafarm specific
    'innovate',
    'users',
    'topics',
    'projects',
    'events',
    'activity',
)

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],

    ## Use this if you have localizable HTML files:
    #'lhtml': [
    #    ('**/templates/**.lhtml',
    #        'tower.management.commands.extract.extract_tower_template'),
    #],

    ## Use this if you have localizable JS files:
    #'javascript': [
        # Make sure that this won't pull in strings from external libraries you
        # may use.
    #    ('media/js/**.js', 'javascript'),
    #],
}

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

## Auth
PWD_ALGORITHM = 'bcrypt'
HMAC_KEYS = {
    '2011-01-01': 'cheesecake',
}

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

## Celery
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'playdoh'
BROKER_PASSWORD = 'playdoh'
BROKER_VHOST = 'playdoh'
BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True

MAX_FILEPATH_LENGTH = 250
USER_AVATAR_PATH = 'img/uploads/avatars/'
TOPIC_IMAGE_PATH = 'img/uploads/topics/'
PROJECT_IMAGE_PATH = 'img/uploads/projects/'
EVENT_IMAGE_PATH = 'img/uploads/events/'

# a list of passwords that meet policy requirements, but are considered
# too common and therefore easily guessed.
PASSWORD_BLACKLIST = (
    'trustno1',
    'access14',
    'rush2112',
    'p@$$w0rd',
    'abcd1234',
    'qwerty123',
)

AUTH_PROFILE_MODULE = 'users.Profile'

# Email goes to the console by default.  s/console/smtp/ for regular delivery
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Innovate Mozilla <innovate@mozilla.org>'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend'
)

BROWSERID_VERIFICATION_URL = 'https://browserid.org/verify'
BROWSERID_CREATE_USER = True
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'
LOGIN_URL = LOGIN_REDIRECT_URL
PROTOCOL = 'https://'
DOMAIN = 'mozillalabs.com'
PORT = 443

PUSH_DEFAULT_HUB = 'http://superfeedr.com/hubbub'
PUSH_DEFAULT_HUB_USERNAME = ''
PUSH_DEFAULT_HUB_PASSWORD = ''
PUSH_CREDENTIALS = 'projects.utils.push_hub_credentials'

SOUTH_TESTS_MIGRATE = False
CACHE_COUNT_TIMEOUT = 60

BLOG_FEED_URL = 'http://blog.mozilla.org/labs/feed/'

# Secure Cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Always generate a CSRF token for anonymous users
ANON_ALWAYS = True

# Django-CSP
CSP_IMG_SRC = (
    "'self'",
    'http://www.mozilla.org',
    'https://www.mozilla.org',
    'http://statse.webtrendslive.com',
    'https://statse.webtrendslive.com',
    'http://www.google.com',
    'https://www.google.com',
    'data:',
)
CSP_STYLE_SRC = (
    "'self'",
    'http://www.mozilla.org',
    'https://www.mozilla.org',
)
CSP_FONT_SRC = (
    "'self'",
    'http://www.mozilla.org',
    'https://www.mozilla.org',
)
CSP_SCRIPT_SRC = (
    "'self'",
    'http://browserid.org',
    'https://browserid.org',
    'http://www.mozilla.org',
    'https://www.mozilla.org',
    'http://statse.webtrendslive.com',
    'https://statse.webtrendslive.com',
    'http://www.google.com',
    'https://www.google.com',
)
CSP_OPTIONS = (
    'eval-script',
)
