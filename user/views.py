from django.shortcuts import render, redirect
from django.views import View

from user.forms import LoginForm, RegisterForm


class LoginView(View):
    template_name = "login.html"  # waiting for html file

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm()
        if form.is_valid():
            form.save()
            return redirect('/experiment/main/')
        return render(request, self.template_name, {"form": form})


class RegistrationView(View):
    template_name = "self.template_name"  # waiting for html file

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm()
        if form.is_valid():
            form.save()
            return redirect('/login/')
        return render(request, self.template_name, {"form": form})


class ResetPasswordView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class LogOutView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class DeleteAccountView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class AboutUsView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
