# Django MemberSuite Authentication Module

[![Build Status](https://travis-ci.org/AASHE/django-membersuite-auth.svg)](https://travis-ci.org/AASHE/django-membersuite-auth)
[![Coverage Status](https://coveralls.io/repos/AASHE/django-membersuite-auth/badge.svg)](https://coveralls.io/github/AASHE/django-membersuite-auth)
[![Code Climate](https://codeclimate.com/github/AASHE/django-membersuite-auth/badges/gpa.svg)](https://codeclimate.com/github/AASHE/django-membersuite-auth)

Version: 0.1

Django authentication backend to authenticate against MemberSuite's
SOAP API.

## Installation

### Dependencies

- Django

- MemberSuite credentials for an API user account


### Installing django-membersuite-auth

```bash
pip install -e git+https://github.com/AASHE/django-membersuite-auth.git#egg=django-membersuite-auth-dev
````

Add to your installed apps:

     INSTALLED_APPS = [
         ...
         'django_membersuite_auth',
         ...
     ]

Update your Authentication Backends:

     AUTHENTICATION_BACKENDS = ('django_membersuite_auth.backends.MemberSuiteBackend',)


### Django settings

- MemberSuite Credentials:

    - `MS_ACCESS_KEY`
    - `MS_SECRET_KEY`
    - `MS_ASSOCIATION_ID`

- `DMA_COOKIE_SESSION`, a name for the MemberSuite auth cookie.

- `DMA_COOKIE_DOMAIN`, a domain, e.g., ".aashe.org", for the cookie.


## Login View Usage

Update template context processors:

     TEMPLATE_CONTEXT_PROCESSORS = (
         "django.core.context_processors.auth",
         "django.core.context_processors.debug",
         "django.core.context_processors.i18n",
         "django.core.context_processors.media",
         "django.core.context_processors.request",
     )

Update your URL configuration file:

     from django_membersuite_auth.views import LoginView, logout

     urlpatterns = [
         ...
         url(r'^login/', LoginView.as_view(), name='login'),
         url(r'^logout/', logout, name='logout'),
         ...
     ]

Include a Login link in your template. Construct the <a> tag such that
it includes a "?next=" parameter like so:

     <a href="{% url "login" %}?next={{ request.path }}">

This will cause your session to redirect back to the page where the
user clicked the Login link after a successful login.

The same is true for logging out:

    <a href="{% url "logout" %}?next={{ request.path }}">
