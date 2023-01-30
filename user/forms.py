from django import forms
from user import models
# Used to encrypt data
from tools.encrypt import md5


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
        model = models.Users
        fields = ["username", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)


class RegisterForm(BootStrapModelForm):
    class Meta:
        model = models.Users
        fields = ["username", "password", "tan"]
