from django.shortcuts import render
from django.views import View


class LoginView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class RegistrationView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


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

