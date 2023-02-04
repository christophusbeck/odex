from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse

from user.models import Users, SecurityQuestions
from django.shortcuts import render, redirect
from django.views import View
from user.forms import LoginForm, RegisterForm, QuestionForm
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
    queryset = SecurityQuestions.objects.all()

    def get(self, request, *args, **kwargs,):
        form = RegisterForm()
        return render(request, self.template_name, {"queryset": self.queryset, "form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(data=request.POST)
        print(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            # form.save()
            return redirect('/login/')
        print("falied")
        return render(request, self.template_name, {"queryset": self.queryset, "form": form})


class CheckUsername(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        check = {
            'flag': Users.objects.filter(username__iexact=username).exists()
        }
        return JsonResponse(check)


class ResetPasswordView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class LogOutView(View):
    template_name = "login.html"  # waiting for html file

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm()
        if form.is_valid():
            form.save()
            return redirect('/login/')
        return render(request, self.template_name, {"form": form})


class DeleteAccountView(View):
    template_name = "login.html"  # waiting for html file

    # still need to handle with deleting
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        def post(self, request, *args, **kwargs):
            form = RegisterForm()
            if form.is_valid():
                form.save()
                return redirect('/login/')
            return render(request, self.template_name, {"form": form})


class AboutUsView(View):
    template_name = ""  # waiting for html file

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class Test(View):
    def get(self, request):
        Users.objects.create(username="tester", password=md5("123"), tan=123)
        return HttpResponse("successful")
