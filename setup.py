#!/usr/bin/env python
from setuptools import setup
import os


# Utility function to read README.md file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name="django-membersuite-auth",
      version="1.3.7",
      description="Django Authentication By MemberSuite",
      author=("Association for the Advancement of Sustainability in "
              "Higher Education"),
      author_email="webdev@aashe.org",
      url="https://github.com/AASHE/django-membersuite-auth",
      long_description=read("README.md"),
      packages=[
          "django_membersuite_auth",
          "django_membersuite_auth.migrations"
      ],
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.5",
          "Framework :: Django"
      ],
      include_package_data=True,
      install_requires=["django",
                        "future",
                        "membersuite-api-client>=0.1.17"]
)  # noqa what's visual indentation?
