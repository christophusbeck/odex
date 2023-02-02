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
    username = forms.CharField(
        label="username",
        max_length=6,
        help_text="Please enter within 6 letters"
    )

    class Meta:
        model = models.Users
        fields = ["password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)


class RegisterForm(BootStrapModelForm):
    repeat_password = forms.CharField(label="Please repeat password", max_length=10)
    security_answer = forms.CharField(label="Please enter your answer", max_length=1024)

    class Meta:
        model = models.Users
        fields = ["username", "password", "tan"]

    def clean(self):
        v1 = self.cleaned_data['password']
        v2 = self.cleaned_data['repeat_password']
        if v1 == v2:
            pass
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('密码输入不一致')
