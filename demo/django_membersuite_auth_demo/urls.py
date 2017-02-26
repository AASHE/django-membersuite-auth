""" urls.py for django_membersuite_auth_demo project.
"""
from django.conf.urls import url, include
from django.contrib import admin

from .views import DemoView


urlpatterns = [
    url(r"^$", DemoView.as_view(), name="demo_view"),
    url(r"^admin/", admin.site.urls),
    url("^", include("django_membersuite_auth.urls"))
]
