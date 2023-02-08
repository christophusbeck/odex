from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse

from user.models import Users, SecurityQuestions, TANs, SecurityAnswers
from django.shortcuts import render, redirect
from django.views import View
from user.forms import LoginForm, RegisterForm, ResetPasswordForm, InitialResetForm
from tools.encrypt import md5


class LoginView(View):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user_obj = Users.objects.filter(**form.cleaned_data).first()
            if not user_obj:
                form.add_error("password", "password error")
                return render(request, self.template_name, {"form": form})
            request.session["info"] = {'id': user_obj.id, 'username': user_obj.username}
            return redirect('/main/')
        return render(request, self.template_name, {"form": form})


class RegistrationView(View):
    template_name = "register.html"

    def get(self, request, *args, **kwargs, ):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            check = TANs.objects.filter(tan__exact=form.cleaned_data.get("tan")).first()
            if not check:
                form.add_error("tan", "invalid tan")
                return render(request, self.template_name, {"form": form})
            elif check.authenticated:
                form.add_error("tan", "tan is used")
                return render(request, self.template_name, {"form": form})

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            question = form.cleaned_data['question']
            security_answer = form.cleaned_data['answer']

            check.authenticated = True
            user = Users()
            user.username = username
            user.password = password
            user.save()

            answer = SecurityAnswers()
            answer.answer = security_answer
            answer.user = user
            answer.question = question
            answer.save()

            return redirect("/login/")

        return render(request, self.template_name, {"form": form})


class CheckUsername(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        check = {
            'flag': Users.objects.filter(username__iexact=username).exists()
        }
        return JsonResponse(check)


class ResetPasswordView(View):
    template_name = "reset_password.html"  # waiting for html file

    def get(self, request, *args, **kwargs):
        initial_form = InitialResetForm()
        form = ResetPasswordForm()
        if request.GET.get('username', False):
            initial_form = InitialResetForm(data=request.GET)
            if initial_form.is_valid():
                user = Users.objects.filter(username=request.GET.get('username')).first()
                if not user:
                    initial_form.add_error("username", "This user does not exist")
                    return render(request, self.template_name, {"initial_form": initial_form})
                security = SecurityAnswers.objects.get(user=user)
                return render(request, self.template_name, {"security": security, "form": form, "initial_form": initial_form})
            return render(request, self.template_name, {"initial_form": initial_form})
        return render(request, self.template_name, {"initial_form": initial_form})

    def post(self, request, *args, **kwargs):
        initial_form = InitialResetForm(data=request.GET)
        form = ResetPasswordForm(data=request.POST)
        user = Users.objects.filter(username=request.GET.get('username')).first()
        security = SecurityAnswers.objects.get(user=user)
        if form.is_valid():
            if security.answer != form.cleaned_data["answer"]:
                form.add_error("answer", "Your answer is wrong")
                return render(request, self.template_name, {"security": security, "form": form, "initial_form": initial_form})
            user.password = form.cleaned_data['password']
            user.save()
            return redirect('/login/')
        return render(request, self.template_name, {"security": security, "form": form, "initial_form": initial_form})


class LogOutView(View):

    def get(self, request, *args, **kwargs):
        request.session.clear()
        return redirect('/login/')


class DeleteAccountView(View):
    def get(self, request, *args, **kwargs):
        info_dict = request.session['info']
        u_id = info_dict['id']
        Users.objects.filter(id=u_id).delete()
        return redirect("/login/")


class AboutUsView(View):
    template_name = "aboutus.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
