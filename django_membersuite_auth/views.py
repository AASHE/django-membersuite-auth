from datetime import datetime, timedelta

import django.contrib.auth.views as standard_auth_views

from django.conf import settings
from django.views.generic import FormView

from .forms import LoginForm


# This is the key we use to cache the MemberSuite session cookie
# in the Django Session object
SESSION_ID_KEY = "membersuite-session-id"


def set_session_id(request, response, session_id):
    cookie = request.COOKIES.get(settings.DMA_COOKIE_SESSION)
    request.session[SESSION_ID_KEY] = session_id
    if cookie != session_id:
        response.set_cookie(settings.DMA_COOKIE_SESSION,
                            session_id,
                            domain=settings.DMA_COOKIE_DOMAIN,
                            expires=datetime.utcnow() + timedelta(days=30))
    return response


def unset_session_id(request, response):
    if SESSION_ID_KEY in request.session:
        del request.session[SESSION_ID_KEY]
    response.delete_cookie(settings.DMA_COOKIE_SESSION,
                           domain=settings.DMA_COOKIE_DOMAIN)
    return response


def login(request, *args, **kwargs):
    response = standard_auth_views.login(request, *args, **kwargs)
    if request.user.is_authenticated():
        if hasattr(request.user, "membersuiteportaluser"):
            membersuite_portal_user = request.user.membersuiteportaluser
            response = set_session_id(
                request,
                response,
                membersuite_portal_user.membersuite_session_key)
    return response


def logout(request, *args, **kwargs):
    delete_cookie = hasattr(request.user, "membersuiteportaluser")
    response = standard_auth_views.logout(request, *args, **kwargs)
    if delete_cookie:
        response = unset_session_id(request, response)
    return response


def logout_then_login(request, *args, **kwargs):
    response = standard_auth_views.logout_then_login(request, *args, **kwargs)
    if hasattr(request.user, "membersuiteportaluser"):
        response = unset_session_id(request, response)
    return response


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def form_valid(self, form):
        return login(self.request)
