from django import forms


class LoginForm(forms.Form):
    """
    Login form
    """

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

