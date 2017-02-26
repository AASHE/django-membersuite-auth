from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    '''Extends the `AuthenticationForm` to use longer usernames'''
    username = forms.CharField(label='Email', max_length=100)
