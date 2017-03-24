from django.views.generic import FormView
from django.contrib.auth.views import login

from .forms import LoginForm


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        return login(self.request)
