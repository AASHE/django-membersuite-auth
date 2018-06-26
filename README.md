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
pip install https://github.com/AASHE/django-membersuite-auth/archive/master.zip
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

### Test environment variables

    - `TEST_MS_PORTAL_USER_ID`
    - `TEST_MS_PORTAL_USER_PASS`
    - `TEST_MS_PORTAL_USER_FIRST_NAME`
    - `TEST_MS_PORTAL_USER_LAST_NAME`
