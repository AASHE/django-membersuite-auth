#!/usr/bin/env python
import os
import sys
import django

BASE_PATH = os.path.dirname(__file__)


def main():
    """Standalone django model test with a
    'memory-only-django-installation'.  You can play with a django
    model without a complete django app installation.
    http://www.djangosnippets.org/snippets/1044/

    """
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings

    global_settings.USE_TZ = True

    global_settings.STATIC_URL = os.environ.get('STATIC_URL', '/static/')
    global_settings.STATIC_ROOT = os.environ.get(
        'STATIC_ROOT',
        os.path.join(BASE_PATH, global_settings.STATIC_URL.strip('/')))

    global_settings.INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django_membersuite_auth'
    )

    global_settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_PATH,
                                 'django-membersuite-auth.sqlite'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

    global_settings.MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware']

    global_settings.SECRET_KEY = "blahblah"

    global_settings.SITE_ID = 1

    global_settings.MS_ACCESS_KEY = os.environ["MS_ACCESS_KEY"]
    global_settings.MS_SECRET_KEY = os.environ["MS_SECRET_KEY"]
    global_settings.MS_ASSOCIATION_ID = os.environ["MS_ASSOCIATION_ID"]

    global_settings.AUTH_USER_MODEL = "auth.User"

    from django.test.utils import get_runner
    test_runner = get_runner(global_settings)

    try:
        django.setup()
    except AttributeError:
        pass

    test_runner = test_runner()
    test_labels = (sys.argv[1:] if len(sys.argv) > 1
                   else ["django_membersuite_auth"])

    failures = test_runner.run_tests(test_labels)

    sys.exit(failures)


if __name__ == '__main__':
    main()
