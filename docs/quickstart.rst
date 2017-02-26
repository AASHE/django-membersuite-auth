.. quickstart:

Tutorial: Using aashe-python in a New Project
=============================================

This is a quick tutorial to get started using the features of
aashe-python in a new project. It covers installing the module in
your ``PYTHONPATH``, setting up your project's settings file, and
some simple use-cases.

.. contents::
   In This Section

Installing aashe-python
-----------------------

The ``aashe-python`` module is written to be an installable Python
package. It is not appropriate to store in the Python Package Index,
however, so simply running ``easy_install aashe-python`` won't work.

The two recommended installation methods are below.

Installing via setup.py
^^^^^^^^^^^^^^^^^^^^^^^

The easiest method, just check out a copy of the aashe-python source
tree and run ``python setup.py``.::

    $ hg clone ssh://hg@bitbucket.org/jesselegg/aashe-python
    $ cd aashe-python
    $ python setup.py

This will install into your system-level Python or the active
virtual environment (virtualenv), if you are using one.

Installing via pip
^^^^^^^^^^^^^^^^^^

To install via pip in a single step use::

    $ pip install -e hg+ssh://hg@bitbucket.org/jesselegg/aashe-python#egg=aashe-python

The advantage to using pip (vs. the setup.py method or
setuptools/easy_install) is that packages can be easily uninstalled
later::

    $ pip uninstall aashe-python

You can also add the path to the aashe-python code to a ``requirements.txt``
file and tell pip to install from that::

    $ cat requirements.txt
    -e hg+ssh://hg@bitbucket.org/jesselegg/aashe-python#egg=aashe-python
    $ pip install -r requirements.txt

Configuring AASHE Modules
--------------------

The next step is to add the relevant aashe-python apps to your Django
project's ``INSTALLED_APPS`` file. For this example, we'll employ
the ``aasheauth``, ``aashetheme``, and ``organization`` apps in our
theoretical project.

Update your ``settings.py`` file like so::

    INSTALLED_APPS = (
        # ... bunch of other Django apps ...
        'aashe.aasheauth',
        'aashe.aashetheme',
        'aashe.organization')

Depending on the needs of the module, some additional configuration may
be needed (see individual module documentation for more information).

Configuring aasheauth
^^^^^^^^^^^^^^^^^^^^^^

The ``aashe.aasheauth`` app has the most configuration. It has several
settings values that are required in order to function (see
:ref:`aasheauth-required-settings` for an explaination). Example settings
follow::

    AASHE_DRUPAL_URI
    AASHE_DRUPAL_DOMAIN
    AASHE_DRUPAL_KEY
    AASHE_DRUPAL_COOKIE_SESSION

.. note::

   These are fake settings values and fake hashes/keys. Refer to Drupal's
   configuration for the correct value for your project.

Configuring aashetheme
^^^^^^^^^^^^^^^^^^^^^^

The ``aashe.aashetheme`` module is very simple to configure. Add it to
your ``INSTALLED_APPS`` setting and that should be it. You can start
writing templates that extend the ``base.html`` or
``base_resources.html`` files. See :ref:`aashetheme-using` for more
details.

If you're using Django's ``staticfiles`` module, you will need to run
the following management command in order to collect the static media
from ``aashe.aashetheme`` and place it in the proper static media
directory::

    $ ./manage.py collectstatic

Configuring organization
^^^^^^^^^^^^^^^^^^^^^^^^

The ``aashe.organization`` app also needs little to no configuration. Add
it to ``INSTALLED_APPS`` and you can start importing the ``Organization``
model into your project's custom apps to use for ``ForeignKeys``, etc. An
example model is below::

    from django.db import models
    from aashe.organization.models import Organization

    # Model for the AASHE Drinking Fountain database:
    # a database of drinking fountain locations on all college
    # campuses in the US. Use it to find a place to fill your water
    # bottle!
    class DrinkingFountain(models.Model):
        campus = models.ForeignKey(Organization)
        fountain_name = models.CharField(max_length=256)
        location_latitude = models.FloatField()
        location_longitude = models.FloatField()
        location_description = models.TextField()

This relates our ``DrinkingFountain`` objects to a specific school via the
``Organization`` model.

Finishing Up
------------

The last remaining configuration step is to run ``syncdb``, which will
create the required tables for each of the aashe-python apps.

Enabling Auth Views
-------------------

In order to establish login and logout views, we may want to add the
``urls.py`` that is included with the ``aasheauth`` module to our
project's own URLs::

    urlpatterns = patterns('',
        ('^accounts/', include('aashe.aasheauth.urls')))

This allows users to immediately login to our new Django project with
their AASHE Account by visiting the URL ``/accounts/login/``.
