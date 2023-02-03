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


class QuestionForm(BootStrapModelForm):
    class Meta:
        model = models.SecurityQuestions
        fields = ["question"]


class RegisterForm(forms.Form):
    repeat_password = forms.CharField(
        label="Please repeat password",
        max_length=64,
        help_text="Please repeat passwords")
    security_answer = forms.CharField(
        label="Please enter your answer",
        max_length=1024,
        help_text="Please enter your answer"
    )
    username = forms.CharField(
        label="username",
        max_length=6,
        help_text="Please enter within 6 letters"
    )
    password = forms.CharField(
        label="password",
        max_length=64,
        help_text="Please enter at least 6 characters"
    )
    tan = forms.IntegerField(
        label="TAN",
        help_text="Please enter 3 characters"
    )
    question = forms.CharField(
        label="Question",
        max_length=64,
        help_text="Please select your question"
    )


    def clean(self):
        v1 = self.cleaned_data.get('password')
        v2 = self.cleaned_data.get('repeat_password')
        if v1 == v2:
            pass
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('Inconsistent password input')

    def clean_repeat_password(self):
        return md5(self.cleaned_data.get("repeat_password"))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)
