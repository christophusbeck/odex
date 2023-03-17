from django import forms
from user import models
from tools.encrypt import md5
from tools.bootstrap import BootStrapForm, BootStrapModelForm


class LoginForm(BootStrapModelForm):
    class Meta:
        model = models.Users
        fields = ["username", "password"]
        widgets = {
            "password": forms.PasswordInput(
                attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'})
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)


class QuestionForm(BootStrapModelForm):
    class Meta:
        model = models.SecurityQuestions
        fields = ["question"]


class RegisterForm(BootStrapForm):
    username = forms.CharField(
        label="username",
        max_length=16,
        help_text="Please enter within 16 letters"
    )
    password = forms.CharField(
        label="password",
        max_length=64,
        min_length=6,
        help_text="Please enter at least 6 characters",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'})
    )
    repeat_password = forms.CharField(
        label="Please repeat password",
        max_length=64,
        min_length=6,
        help_text="Please repeat passwords",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'repeat_password'})
    )
    tan = forms.CharField(
        label="TAN",
        help_text="Please enter a valid 3-digit tan number"
    )
    question = forms.ModelChoiceField(
        label="Question",
        queryset=models.SecurityQuestions.objects.all(),
        help_text="Please select your question"
    )
    answer = forms.CharField(
        label="Please enter your answer",
        max_length=1024,
        help_text="Please enter your answer"
    )

    def clean(self):
        v1 = self.cleaned_data.get('password')
        v2 = self.cleaned_data.get('repeat_password')
        if v1 == v2:
            pass
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('Inconsistent password input.')

    def clean_repeat_password(self):
        return md5(self.cleaned_data.get("repeat_password"))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)


class InitialResetForm(BootStrapForm):
    username = forms.CharField(
        label="username",
        max_length=16,
        help_text="Please enter within 16 letters"
    )

class ResetPasswordForm(BootStrapForm):
    password = forms.CharField(
        label="password",
        max_length=64,
        min_length=6,
        help_text="Please enter at least 6 characters",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'})
    )
    repeat_password = forms.CharField(
        label="Please repeat password",
        max_length=64,
        min_length=6,
        help_text="Please repeat passwords",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'repeat_password'})
    )
    answer = forms.CharField(
        label="Please enter your answer",
        max_length=1024,
        help_text="Please enter your answer"
    )

    def clean(self):
        v1 = self.cleaned_data.get('password')
        v2 = self.cleaned_data.get('repeat_password')
        if v1 == v2:
            pass
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('Inconsistent password input.')

    def clean_repeat_password(self):
        return md5(self.cleaned_data.get("repeat_password"))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return md5(password)


class ChangeNameForm(BootStrapModelForm):
    class Meta:
        model = models.Users
        fields = ["username"]


class InitialChangePasswordForm(BootStrapForm):
    old_password = forms.CharField(
        label="password",
        max_length=64,
        help_text="Please enter your old password",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'})
    )

    def clean_old_password(self):
        password = self.cleaned_data.get("old_password")
        return md5(password)

class ChangePasswordForm(BootStrapForm):
    new_password = forms.CharField(
        label="password",
        max_length=64,
        min_length=6,
        help_text="Please enter at least 6 characters",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'password'})
    )
    repeat_password = forms.CharField(
        label="Please repeat password",
        max_length=64,
        min_length=6,
        help_text="Please repeat passwords",
        widget=forms.PasswordInput(
            attrs={'placeholder': '********', 'autocomplete': 'off', 'data-toggle': 'repeat_password'})
    )

    def clean(self):
        v1 = self.cleaned_data.get('new_password')
        v2 = self.cleaned_data.get('repeat_password')
        if v1 == v2:
            pass
        else:
            from django.core.exceptions import ValidationError
            raise ValidationError('Inconsistent password input.')

    def clean_repeat_password(self):
        return md5(self.cleaned_data.get("repeat_password"))

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        return md5(password)






