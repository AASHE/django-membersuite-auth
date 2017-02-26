try:
    from django.conf.urls.defaults import url
except ImportError:  # Django >= 1.6
    from django.conf.urls import url

from .forms import LoginForm
from .views import login, logout_then_login


def get_patterns():
    """Returns the `patterns` function for this version of Django.

    It lives in django.conf.urs.defaults in < v1.6, in
    django.conf.urls in >= v1.6 && < 1.10, and in >= v1.10,
    it's completely gone.

    When no `patterns` can be imported (i.e., when Django version >=
    1.10) one is defined.  It just creates a list of its arguments.  A
    list is all >= v1.10 wants.

    """
    try:
        from django.conf.urls.defaults import patterns
    except ImportError:  # Django >= 1.6
        try:
            from django.conf.urls import patterns
        except ImportError:  # Django >= 1.10
            def patterns(*urls):
                return list(urls)
    return patterns


urlpatterns = get_patterns()(

    url(r"^login/$",
        login, {"template_name": "login.html",
                "authentication_form": LoginForm},
        name="django_membersuite_auth_login"),

    url(r"^logout/$",
        logout_then_login,
        name="django_membersuite_auth_logout"))
