from django import forms

from user import models


class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label
                }


class LoginForm(BootStrapModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["username", "password"]


class RegisterForm(BootStrapModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["username", "password", "tan"]
