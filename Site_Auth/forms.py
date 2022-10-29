from django import forms

from Site_User.models import User


class newForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        label="Username",
        widget=forms.TextInput(
            attrs={"class": "form-control", "onfocus": "focused(this)", "onfocusout": "defocused(this)"}))