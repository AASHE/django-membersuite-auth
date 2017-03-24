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

The ``django-membersuite-auth`` module requires the following settings:

.. _authentication-views:

Authentication Views
--------------------

The authentication app includes a set of views for logging users in and
out. These views are basically identical to Django's built-in auth views
with some small alterations.

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
