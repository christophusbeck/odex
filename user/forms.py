from django import forms

from user import models


class UserModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["username", "password"]
        widgets = {
            "usename": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}