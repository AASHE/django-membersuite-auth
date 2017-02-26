.. _aasheauth:
.. module:: aashe.aasheauth

AASHE Accounts Support
======================

The ``aashe.aasheauth`` module is a Django app that provides support
for authenticating users in Django using their Drupal credentials
("AASHE Account"). This generally involves mapping a Drupal user id
(UID) to a Django User object by way of XML-RPC calls to Drupal User
Services.

.. contents::
   In This Section

.. _authentication-backend-django:

Django Authentication Backend
-----------------------------

.. class:: backends.AASHEBackend

   A generic, reusable backend for authenticating AASHE Django
   projects against the ``aashe.aasheauth.services.AASHEUserService``.
   Expects the XML-RPC service to return a user dictionary that contains
   all Drupal profile information.

   Uses the :class:`AASHEUser` model to translate
   between Drupal UID's and Django User objects. This backend also supports
   mixed Django/Drupal ID schemes (ie. you can login as a Drupal user
   or a Django user).

To use this custom backend in a Django project:

Add the ``aashe.aasheauth`` app to your ``INSTALLED_APPS``
setting. Next, add the AASHE account backend to the
``AUTHENTICATION_BACKENDS`` setting. For example::

    AUTHENTICATION_BACKENDS = ('aashe.aasheauth.backends.AASHEBackend',)

.. _aasheauth-required-settings:

Required Settings
-----------------

The ``aasheauth`` module requires the following settings:

``AASHE_AUTH_USER_SERVICE_URI``
    This is the URI endpoint for the AASHE XML-RPC Drupal Services
    module. E.g. ``http://www.aashe.org/services/xmlrpc``.

``AASHE_AUTH_USER_SERVICE_KEY``
    This is the API key used by the XML-RPC Drupal Services module to
    authenticate the calling application has legitimate access. This
    is a long hash value like ``21de119812a4f54200aec862c73cf2ee``.

``AASHE_AUTH_KEY_DOMAIN``
    The domain used in the signing operation required by the Drupal
    Services XML-RPC module. Something like: ``acupcc.aashe.org`` or
    ``stars.aashe.org``. This must match the domain specified
    in the key created in the Drupal Services module.

``AASHE_AUTH_COOKIE_SESSION``
    The name of the Drupal session cookie, this is a value like
    ``SESS119812a4f54200aec862c73cf2ee``. Required by the
    :ref:`aashe-account-middleware`.

``AASHE_AUTH_COOKIE_DOMAIN``
    The domain to use when setting the Drupal cookie for single sign-on
    use case. Used when the user signs-in to Django first to ensure
    Drupal also sees them as being signed-in. Should probably be
    something like ``.aashe.org``.

.. _authentication-views:

Authentication Views
--------------------

The authentication app includes a set of views for logging users in and
out. These views are basically identical to Django's built-in auth views
with some small alterations.

.. function:: views.login

   A wrapper around ``django.contrib.auth.views.login`` that sets a
   Drupal session cookie if it's not present, allowing for
   single sign-on.

.. function:: views.logout

   A wrapper around ``django.contrib.auth.views.logout`` that unsets
   a Drupal session cookie if it's present, allowing for single
   "sign-out."

.. function:: views.logout_then_login

   A wrapper around ``django.contrib.auth.views.logout_then_login`` that
   unsets a Drupal session cooke if it's present, allowing for single
   "sign-out."

URL patterns for these views are also provided. To use these views in
a project and get automatic AASHE Account support, you can use the
provided ``urls.py`` or write your own. For example, add the following
to your project's urls.py::

    urlpatterns = patterns('',
        ('^accounts/', include('aashe.aasheauth.urls')),
        # Other project URLs ...
    )

.. _the-aasheuser-model:

The AAHSEUser Model
-------------------

In order to maintain a relationship between Drupal users and Django users,
the ``aasheauth`` module uses a simple model to store the Drupal User ID
and the Django ``User`` object.

.. class:: models.AASHEUser

    The ``AASHEUser`` model contains three fields:

    ``user``
        A OneToOneField to the built-in Django user model (
        ``django.contrib.auth.models.User``).

    ``drupal_id``
        The integer value of the Drupal user ID (UID).

    ``drupal_session_key``
        The Drupal session key for the user. This is used by
        :ref:`authentication-views` to perform single sign-on from
        the Django side.

.. _validating-drupal-users:

Validating Drupal Users
-----------------------

The AASHEBackend supports a "validator" object for Drupal users signing-in
to Django. The ``DefaultDrupalValidator`` is the default validator used
if no other validator is specified in the project's settings file.

Custom validators can be written that do more complex processing of
Drupal users. A validator class has one requirement: implement a
``validate`` method that takes as its only argument a dictionary
representing the Drupal user data returned from XML-RPC.

Custom validators can be specified with the ``AASHE_DRUPAL_VALIDATOR``
setting. This is a string representing the import path to the custom
validator class. For example::

    AASHE_DRUPAL_VALIDATOR = "acupcc.usermanager.MyValidator"

.. class:: backends.DefaultDrupalValidator

   This default validator is very simple. When a Drupal user signs-in to
   the Django site, it checks for an ``AASHE_DRUPAL_REQUIRED_ROLES``
   setting in the Django settings file. This setting is a tuple of Drupal
   roles the user must have in order to sign-in to the Django site. The
   user must have at least one of these roles. If no roles setting is
   specified, the default is to allow all Drupal users to sign-in.::

       AASHE_DRUPAL_REQUIRED_ROLES = ('pcc basic', 'pcc admin')

.. _aashe-account-middleware:

AASHE Account Middleware
------------------------

The ``aasheauth`` module provide Django middleware for detecting when
users are signed-in to the primary aashe.org Drupal site and automatically
signs them in to the Django site as well.

.. class:: middleware.AASHEAccountMiddleware

   Middleware that inspects the request object looking for a Drupal
   session key from the primary AASHE site.

   For performance, the middleware only attempts to sign-in an
   anonymous Django user that has a Drupal session key *one* time. If
   that sign-in fails, the Drupal session key is cached in the
   anonymous Django user's session object, which prevents the middleware
   from trying to sign-in subsequent requests.

   When the middleware attempts to sign-in an anonymous user, the
   process is as follows:

   1. Request comes in to the middleware
   2. Middleware makes an XML-RPC call to Drupal's ``aasheuser.current``
      function with the "sniffed" session key. If no Drupal user is
      returned, it means the session key is invalid and the middleware ends.
   3. If the XML-RPC service returns Drupal user information (as a
      dictionary), the middlware runs it through the validation process
      (see :ref:`validating-drupal-users`).
   4. If the Drupal user passes the validation process, the middleware
      takes the Drupal UID from the user dictionary and passes it to
      ``AASHEBackend``, which authenticates the Drupal user.
   5. If no ``User`` or ``AASHEUser`` objects exist for this Drupal
      user yet, they are automatically created and marked active.
   6. If the Django user that matches the Drupal UID is active, they
      are signed-in.

.. note::

   This middleware (and single sign-on support in general) will only
   work for AASHE projects on the same domain. This is not a limitation of
   the authentication app, but is due to the security feature in browsers
   that prevents cross-domain cookie reading and writing.

To use the middlware simply add
``aashe.aasheauth.middleware.AASHEAccountMiddleware`` to your
project's ``MIDDLEWARE_CLASSES`` setting somewhere *AFTER* the
``django.contrib.auth.middleware.AuthenticationMiddleware``. This middleware
requires Django's built-in ``AuthenticationMiddleware``. Once added,
single sign-on with AASHE Accounts will be instantly available to your
project.

Single Sign-on Support
^^^^^^^^^^^^^^^^^^^^^^

The authentication app supports "single sign-on" by inspecting the user's
cookies, looking for a valid Drupal session key, and logging that user
into Django. Any Drupal user that is logged-in to Drupal and passes the
validation requirements will be logged-in to Django automatically.

Users that login to the AASHE Drupal site, will be logged into any
projects using the ``aasheauth`` app. Likewise, any users that sign-in
to a project using the ``aasheauth`` app will be signed-in to Drupal as
well as all other projects that use the ``aasheauth`` app.

Logging-out of a project that uses ``aasheauth`` will also logout the
user from Drupal (and other ``aasheauth`` app projects).
